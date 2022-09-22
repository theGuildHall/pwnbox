import imp
import importlib
import os
import sys
import threading
import time
import traceback
import zipfile

import sublime
import sublime_api


api_ready = False

deferred_plugin_loadeds = []

application_command_classes = []
window_command_classes = []
text_command_classes = []

view_event_listener_classes = []
view_event_listeners = {}

all_command_classes = [
    application_command_classes,
    window_command_classes,
    text_command_classes]

all_callbacks = {
    'on_new': [],
    'on_clone': [],
    'on_load': [],
    'on_pre_close': [],
    'on_close': [],
    'on_pre_save': [],
    'on_post_save': [],
    'on_modified': [],
    'on_selection_modified': [],
    'on_activated': [],
    'on_deactivated': [],
    'on_query_context': [],
    'on_query_completions': [],
    'on_hover': [],
    'on_text_command': [],
    'on_window_command': [],
    'on_post_text_command': [],
    'on_post_window_command': [],
    'on_modified_async': [],
    'on_selection_modified_async': [],
    'on_pre_save_async': [],
    'on_post_save_async': [],
    'on_activated_async': [],
    'on_deactivated_async': [],
    'on_new_async': [],
    'on_load_async': [],
    'on_clone_async': []}

pending_on_activated_async_lock = threading.Lock()

pending_on_activated_async_callbacks = {
    'EventListener': [],
    'ViewEventListener': []}

profile = {}


def unload_module(module):
    if "plugin_unloaded" in module.__dict__:
        try:
            module.plugin_unloaded()
        except:
            traceback.print_exc()

    # Check unload_handler too, for backwards compat
    if "unload_handler" in module.__dict__:
        try:
            module.unload_handler()
        except:
            traceback.print_exc()

    # Unload the old plugins
    if "__plugins__" in module.__dict__:
        for view_id, listener_instances in view_event_listeners.items():
            for vel in listener_instances[:]:
                if vel.__class__ in module.__plugins__:
                    listener_instances.remove(vel)

        for p in module.__plugins__:
            for cmd_cls_list in all_command_classes:
                try:
                    cmd_cls_list.remove(p)
                except ValueError:
                    pass
            for c in all_callbacks.values():
                try:
                    c.remove(p)
                except ValueError:
                    pass

            try:
                view_event_listener_classes.remove(p)
            except ValueError:
                pass


def unload_plugin(modulename):
    print("unloading plugin", modulename)

    was_loaded = modulename in sys.modules
    if was_loaded:
        m = sys.modules[modulename]
        unload_module(m)
        del sys.modules[modulename]


def reload_plugin(modulename):
    print("reloading plugin", modulename)

    if modulename in sys.modules:
        m = sys.modules[modulename]
        unload_module(m)
        m = imp.reload(m)
    else:
        m = importlib.import_module(modulename)

    load_module(m)


def load_module(m):
    module_plugins = []
    on_activated_targets = []
    vel_on_activated_classes = []
    el_on_activated_async_targets = []
    vel_on_activated_async_targets = []
    module_view_event_listener_classes = []
    for type_name in dir(m):
        try:
            t = m.__dict__[type_name]
            if t.__bases__:
                is_plugin = False
                if issubclass(t, ApplicationCommand):
                    application_command_classes.append(t)
                    is_plugin = True
                if issubclass(t, WindowCommand):
                    window_command_classes.append(t)
                    is_plugin = True
                if issubclass(t, TextCommand):
                    text_command_classes.append(t)
                    is_plugin = True

                if is_plugin:
                    module_plugins.append(t)

                if issubclass(t, EventListener):
                    obj = t()
                    for p in all_callbacks.items():
                        if p[0] in dir(obj):
                            p[1].append(obj)

                    if "on_activated" in dir(obj):
                        on_activated_targets.append(obj)

                    if "on_activated_async" in dir(obj):
                        el_on_activated_async_targets.append(obj)

                    module_plugins.append(obj)

                if issubclass(t, ViewEventListener):
                    view_event_listener_classes.append(t)
                    module_view_event_listener_classes.append(t)
                    if "on_activated" in dir(t):
                        vel_on_activated_classes.append(t)
                    if "on_activated_async" in dir(t):
                        vel_on_activated_async_targets.append(t)
                    module_plugins.append(t)

        except AttributeError:
            pass

    if el_on_activated_async_targets or vel_on_activated_async_targets:
        with pending_on_activated_async_lock:
            pending_on_activated_async_callbacks['EventListener'].extend(
                el_on_activated_async_targets
            )
            pending_on_activated_async_callbacks['ViewEventListener'].extend(
                vel_on_activated_async_targets
            )

    if len(module_plugins) > 0:
        m.__plugins__ = module_plugins

    if api_ready:
        if "plugin_loaded" in m.__dict__:
            try:
                m.plugin_loaded()
            except:
                traceback.print_exc()

        # Create any require ViewEventListener objects
        if len(module_view_event_listener_classes) > 0:
            for w in sublime.windows():
                for v in w.views():
                    create_view_event_listeners(
                        module_view_event_listener_classes, v)

        # Synthesize any required on_activated calls
        w = sublime.active_window()
        if w:
            v = w.active_view()
            if v:
                for el in on_activated_targets:
                    try:
                        el.on_activated(v)
                    except:
                        traceback.print_exc()

                for vel_cls in vel_on_activated_classes:
                    vel = find_view_event_listener(v, vel_cls)
                    if not vel:
                        continue
                    try:
                        vel.on_activated()
                    except:
                        traceback.print_exc()

    elif "plugin_loaded" in m.__dict__:
        deferred_plugin_loadeds.append(m.plugin_loaded)


def synthesize_on_activated_async():
    if not api_ready:
        return

    with pending_on_activated_async_lock:
        els = pending_on_activated_async_callbacks['EventListener']
        vels = pending_on_activated_async_callbacks['ViewEventListener']
        pending_on_activated_async_callbacks['EventListener'] = []
        pending_on_activated_async_callbacks['ViewEventListener'] = []

    for el in els:
        w = sublime.active_window()
        if not w:
            continue
        v = w.active_view()
        if not v:
            continue
        try:
            el.on_activated_async(v)
        except:
            traceback.print_exc()

    for vel_cls in vels:
        w = sublime.active_window()
        if not w:
            continue
        v = w.active_view()
        if not v:
            continue
        vel = find_view_event_listener(v, vel_cls)
        if not vel:
            continue
        try:
            vel.on_activated_async()
        except:
            traceback.print_exc()


def create_application_commands():
    cmds = []
    for class_ in application_command_classes:
        cmds.append(class_())
    sublime_api.notify_application_commands(cmds)


def create_window_commands(window_id):
    window = sublime.Window(window_id)
    cmds = []
    for class_ in window_command_classes:
        cmds.append(class_(window))
    return cmds


def create_text_commands(view_id):
    view = sublime.View(view_id)
    cmds = []
    for class_ in text_command_classes:
        cmds.append(class_(view))
    return cmds


def on_api_ready():
    global api_ready
    api_ready = True

    for plc in deferred_plugin_loadeds:
        try:
            plc()
        except:
            traceback.print_exc()
    deferred_plugin_loadeds.clear()

    # Create ViewEventListener instances
    if len(view_event_listener_classes) > 0:
        for w in sublime.windows():
            for v in w.views():
                attach_view(v)

    # Synthesize an on_activated call
    w = sublime.active_window()
    if w:
        view_id = sublime_api.window_active_view(w.window_id)
        if view_id != 0:
            try:
                on_activated(view_id)
            except:
                traceback.print_exc()


def is_view_event_listener_applicable(cls, view):
    if not cls.is_applicable(view.settings()):
        return False

    if cls.applies_to_primary_view_only() and not view.is_primary():
        return False

    return True


def create_view_event_listeners(classes, view):
    if len(classes) > 0:
        if view.view_id not in view_event_listeners:
            view_event_listeners[view.view_id] = []

        for c in classes:
            if is_view_event_listener_applicable(c, view):
                view_event_listeners[view.view_id].append(c(view))


def check_view_event_listeners(view):
    if len(view_event_listener_classes) > 0:
        if view.view_id not in view_event_listeners:
            view_event_listeners[view.view_id] = []

        listeners = view_event_listeners[view.view_id]

        for cls in view_event_listener_classes:
            found = False
            instance = None
            for l in listeners:
                if l.__class__ == cls:
                    found = True
                    instance = l
                    break

            want = is_view_event_listener_applicable(cls, view)

            if want and not found:
                listeners.append(cls(view))
            elif found and not want:
                listeners.remove(instance)


def attach_view(view):
    check_view_event_listeners(view)

    view.settings().add_on_change(
        "check_view_event_listeners",
        lambda: check_view_event_listeners(view))


check_all_view_event_listeners_scheduled = False


def check_all_view_event_listeners():
    global check_all_view_event_listeners_scheduled
    check_all_view_event_listeners_scheduled = False
    for w in sublime.windows():
        for v in w.views():
            check_view_event_listeners(v)


def detach_view(view):
    if view.view_id in view_event_listeners:
        del view_event_listeners[view.view_id]

    # A view has closed, which implies 'is_primary' may have changed, so see if
    # any of the ViewEventListener classes need to be created.
    # Call this in a timeout, as 'view' will still be reporting itself as a
    # primary at this stage
    global check_all_view_event_listeners_scheduled
    if not check_all_view_event_listeners_scheduled:
        check_all_view_event_listeners_scheduled = True
        sublime.set_timeout(check_all_view_event_listeners)


def event_listeners_for_view(view):
    if view.view_id in view_event_listeners:
        return view_event_listeners[view.view_id]
    else:
        return []


def find_view_event_listener(view, cls):
    if view.view_id in view_event_listeners:
        for vel in view_event_listeners[view.view_id]:
            if vel.__class__ == cls:
                return vel
    return None


def on_new(view_id):
    v = sublime.View(view_id)

    attach_view(v)

    for callback in all_callbacks['on_new']:
        try:
            callback.on_new(v)
        except:
            traceback.print_exc()


def on_new_async(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_new_async']:
        try:
            callback.on_new_async(v)
        except:
            traceback.print_exc()


def on_clone(view_id):
    v = sublime.View(view_id)

    attach_view(v)

    for callback in all_callbacks['on_clone']:
        try:
            callback.on_clone(v)
        except:
            traceback.print_exc()


def on_clone_async(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_clone_async']:
        try:
            callback.on_clone_async(v)
        except:
            traceback.print_exc()


class Summary(object):
    def __init__(self):
        self.max = 0.0
        self.sum = 0.0
        self.count = 0

    def record(self, x):
        self.count += 1
        self.sum += x
        self.max = max(self.max, x)

    def __str__(self):
        if self.count > 1:
            return "{0:.3f}s total, mean: {1:.3f}s, max: {2:.3f}s".format(self.sum, self.sum / self.count, self.max)
        elif self.count == 1:
            return "{0:.3f}s total".format(self.sum)
        else:
            return "0s total"


def run_callback(event, callback, expr):
    t0 = time.time()

    try:
        expr()
    except:
        traceback.print_exc()

    elapsed = time.time() - t0

    if event not in profile:
        profile[event] = {}

    p = profile[event]

    name = callback.__module__
    if name not in p:
        p[name] = Summary()

    p[name].record(elapsed)


def run_view_listener_callback(view, name):
    for vel in event_listeners_for_view(view):
        if name in vel.__class__.__dict__:
            run_callback(name, vel, lambda: vel.__class__.__dict__[name](vel))


def run_async_view_listener_callback(view, name):
    for vel in event_listeners_for_view(view):
        if name in vel.__class__.__dict__:
            try:
                vel.__class__.__dict__[name](vel)
            except:
                traceback.print_exc()


def on_load(view_id):
    v = sublime.View(view_id)

    attach_view(v)

    for callback in all_callbacks['on_load']:
        run_callback('on_load', callback, lambda: callback.on_load(v))
    run_view_listener_callback(v, 'on_load')


def on_load_async(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_load_async']:
        try:
            callback.on_load_async(v)
        except:
            traceback.print_exc()
    run_async_view_listener_callback(v, 'on_load_async')


def on_pre_close(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_pre_close']:
        run_callback('on_pre_close', callback, lambda: callback.on_pre_close(v))
    run_view_listener_callback(v, 'on_pre_close')


def on_close(view_id):
    v = sublime.View(view_id)

    run_view_listener_callback(v, 'on_close')
    detach_view(v)

    for callback in all_callbacks['on_close']:
        run_callback('on_close', callback, lambda: callback.on_close(v))


def on_pre_save(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_pre_save']:
        run_callback('on_pre_save', callback, lambda: callback.on_pre_save(v))
    run_view_listener_callback(v, 'on_pre_save')


def on_pre_save_async(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_pre_save_async']:
        try:
            callback.on_pre_save_async(v)
        except:
            traceback.print_exc()
    run_async_view_listener_callback(v, 'on_pre_save_async')


def on_post_save(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_post_save']:
        run_callback('on_post_save', callback, lambda: callback.on_post_save(v))
    run_view_listener_callback(v, 'on_post_save')


def on_post_save_async(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_post_save_async']:
        try:
            callback.on_post_save_async(v)
        except:
            traceback.print_exc()
    run_async_view_listener_callback(v, 'on_post_save_async')


def on_modified(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_modified']:
        run_callback('on_modified', callback, lambda: callback.on_modified(v))
    run_view_listener_callback(v, 'on_modified')


def on_modified_async(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_modified_async']:
        try:
            callback.on_modified_async(v)
        except:
            traceback.print_exc()
    run_async_view_listener_callback(v, 'on_modified_async')


def on_selection_modified(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_selection_modified']:
        run_callback('on_selection_modified', callback, lambda: callback.on_selection_modified(v))
    run_view_listener_callback(v, 'on_selection_modified')


def on_selection_modified_async(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_selection_modified_async']:
        try:
            callback.on_selection_modified_async(v)
        except:
            traceback.print_exc()
    run_async_view_listener_callback(v, 'on_selection_modified_async')


def on_activated(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_activated']:
        run_callback('on_activated', callback, lambda: callback.on_activated(v))
    run_view_listener_callback(v, 'on_activated')


def on_activated_async(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_activated_async']:
        try:
            callback.on_activated_async(v)
        except:
            traceback.print_exc()
    run_async_view_listener_callback(v, 'on_activated_async')


def on_deactivated(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_deactivated']:
        run_callback('on_deactivated', callback, lambda: callback.on_deactivated(v))
    run_view_listener_callback(v, 'on_deactivated')


def on_deactivated_async(view_id):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_deactivated_async']:
        try:
            callback.on_deactivated_async(v)
        except:
            traceback.print_exc()
    run_async_view_listener_callback(v, 'on_deactivated_async')


def on_query_context(view_id, key, operator, operand, match_all):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_query_context']:
        try:
            val = callback.on_query_context(v, key, operator, operand, match_all)
            if val:
                return True
        except:
            traceback.print_exc()

    for vel in event_listeners_for_view(v):
        if 'on_query_context' in vel.__class__.__dict__:
            try:
                val = vel.on_query_context(key, operator, operand, match_all)
                if val:
                    return True
            except:
                traceback.print_exc()

    return False


def normalise_completion(c):
    if len(c) == 1:
        return (c[0], "", "")
    elif len(c) == 2:
        return (c[0], "", c[1])
    else:
        return c


def on_query_completions(view_id, prefix, locations):
    v = sublime.View(view_id)

    completions = []
    flags = 0
    for callback in all_callbacks['on_query_completions']:
        try:
            res = callback.on_query_completions(v, prefix, locations)

            if isinstance(res, tuple):
                completions += [normalise_completion(c) for c in res[0]]
                flags |= res[1]
            elif isinstance(res, list):
                completions += [normalise_completion(c) for c in res]
        except:
            traceback.print_exc()

    for vel in event_listeners_for_view(v):
        if 'on_query_completions' in vel.__class__.__dict__:
            try:
                res = vel.on_query_completions(prefix, locations)

                if isinstance(res, tuple):
                    completions += [normalise_completion(c) for c in res[0]]
                    flags |= res[1]
                elif isinstance(res, list):
                    completions += [normalise_completion(c) for c in res]
            except:
                traceback.print_exc()

    return (completions, flags)


def on_hover(view_id, point, hover_zone):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_hover']:
        run_callback('on_hover', callback, lambda: callback.on_hover(v, point, hover_zone))

    for vel in event_listeners_for_view(v):
        if 'on_hover' in vel.__class__.__dict__:
            try:
                vel.on_hover(point, hover_zone)
            except:
                traceback.print_exc()


def on_text_command(view_id, name, args):
    v = sublime.View(view_id)

    for vel in event_listeners_for_view(v):
        if 'on_text_command' in vel.__class__.__dict__:
            try:
                res = vel.on_text_command(name, args)
                if isinstance(res, tuple):
                    return res
                elif res:
                    return (res, None)
            except:
                traceback.print_exc()

    for callback in all_callbacks['on_text_command']:
        try:
            res = callback.on_text_command(v, name, args)
            if isinstance(res, tuple):
                return res
            elif res:
                return (res, None)
        except:
            traceback.print_exc()

    return ("", None)


def on_window_command(window_id, name, args):
    window = sublime.Window(window_id)
    for callback in all_callbacks['on_window_command']:
        try:
            res = callback.on_window_command(window, name, args)
            if isinstance(res, tuple):
                return res
            elif res:
                return (res, None)
        except:
            traceback.print_exc()

    return ("", None)


def on_post_text_command(view_id, name, args):
    v = sublime.View(view_id)
    for callback in all_callbacks['on_post_text_command']:
        try:
            callback.on_post_text_command(v, name, args)
        except:
            traceback.print_exc()

    for vel in event_listeners_for_view(v):
        if 'on_post_text_command' in vel.__class__.__dict__:
            try:
                vel.on_post_text_command(name, args)
            except:
                traceback.print_exc()


def on_post_window_command(window_id, name, args):
    window = sublime.Window(window_id)
    for callback in all_callbacks['on_post_window_command']:
        try:
            callback.on_post_window_command(window, name, args)
        except:
            traceback.print_exc()


class CommandInputHandler(object):
    def name(self):
        clsname = self.__class__.__name__
        name = clsname[0].lower()
        last_upper = False
        for c in clsname[1:]:
            if c.isupper() and not last_upper:
                name += '_'
                name += c.lower()
            else:
                name += c
            last_upper = c.isupper()
        if name.endswith("_input_handler"):
            name = name[0:-14]
        return name

    def next_input(self, args):
        return None

    def placeholder(self):
        return ""

    def initial_text(self):
        return ""

    def preview(self, arg):
        return ""

    def validate(self, arg):
        return True

    def cancel(self):
        pass

    def confirm(self, arg):
        pass

    def create_input_handler_(self, args):
        return self.next_input(args)

    def preview_(self, v):
        ret = self.preview(v)

        if ret is None:
            return ("", 0)
        elif isinstance(ret, sublime.Html):
            return (ret.data, 1)
        else:
            return (ret, 0)

    def validate_(self, v):
        return self.validate(v)

    def cancel_(self):
        self.cancel()

    def confirm_(self, v):
        self.confirm(v)


class BackInputHandler(CommandInputHandler):
    def name(self):
        return "_Back"


class TextInputHandler(CommandInputHandler):
    def description(self, text):
        return text

    def setup_(self, args):
        props = {
            "initial_text": self.initial_text(),
            "placeholder_text": self.placeholder(),
            "type": "text",
        }

        return ([], props)

    def description_(self, v, text):
        return self.description(text)


class ListInputHandler(CommandInputHandler):
    def list_items(self):
        return []

    def description(self, v, text):
        return text

    def setup_(self, args):
        items = self.list_items()

        selected_item_index = -1

        if isinstance(items, tuple):
            items, selected_item_index = items

        for i in range(len(items)):
            it = items[i]
            if isinstance(it, str):
                items[i] = (it, it)

        props = {
            "initial_text": self.initial_text(),
            "placeholder_text": self.placeholder(),
            "selected": selected_item_index,
            "type": "list",
        }

        return (items, props)

    def description_(self, v, text):
        return self.description(v, text)


class Command(object):
    def name(self):
        clsname = self.__class__.__name__
        name = clsname[0].lower()
        last_upper = False
        for c in clsname[1:]:
            if c.isupper() and not last_upper:
                name += '_'
                name += c.lower()
            else:
                name += c
            last_upper = c.isupper()
        if name.endswith("_command"):
            name = name[0:-8]
        return name

    def is_enabled_(self, args):
        ret = None
        try:
            args = self.filter_args(args)
            if args:
                ret = self.is_enabled(**args)
            else:
                ret = self.is_enabled()
        except TypeError:
            ret = self.is_enabled()

        if not isinstance(ret, bool):
            raise ValueError("is_enabled must return a bool", self)

        return ret

    def is_enabled(self):
        return True

    def is_visible_(self, args):
        ret = None
        try:
            args = self.filter_args(args)
            if args:
                ret = self.is_visible(**args)
            else:
                ret = self.is_visible()
        except TypeError:
            ret = self.is_visible()

        if not isinstance(ret, bool):
            raise ValueError("is_visible must return a bool", self)

        return ret

    def is_visible(self):
        return True

    def is_checked_(self, args):
        ret = None
        try:
            args = self.filter_args(args)
            if args:
                ret = self.is_checked(**args)
            else:
                ret = self.is_checked()
        except TypeError:
            ret = self.is_checked()

        if not isinstance(ret, bool):
            raise ValueError("is_checked must return a bool", self)

        return ret

    def is_checked(self):
        return False

    def description_(self, args):
        try:
            args = self.filter_args(args)
            if args is not None:
                return self.description(**args)
            else:
                return self.description()
        except TypeError:
            return ""

    def description(self):
        return ""

    def filter_args(self, args):
        if args:
            if 'event' in args and not self.want_event():
                args = args.copy()
                del args['event']

        return args

    def want_event(self):
        return False

    def input(self, args):
        return None

    def input_description(self):
        return ""

    def create_input_handler_(self, args):
        return self.input(args)


class ApplicationCommand(Command):
    def run_(self, edit_token, args):
        args = self.filter_args(args)
        try:
            if args:
                return self.run(**args)
            else:
                return self.run()
        except (TypeError) as e:
            if 'required positional argument' in str(e):
                if sublime_api.can_accept_input(self.name(), args):
                    sublime.active_window().run_command(
                        'show_overlay',
                        {
                            'overlay': 'command_palette',
                            'command': self.name(),
                            'args': args
                        }
                    )
                    return
            raise

    def run(self):
        pass


class WindowCommand(Command):
    def __init__(self, window):
        self.window = window

    def run_(self, edit_token, args):
        args = self.filter_args(args)
        try:
            if args:
                return self.run(**args)
            else:
                return self.run()
        except (TypeError) as e:
            if 'required positional argument' in str(e):
                if sublime_api.window_can_accept_input(self.window.id(), self.name(), args):
                    sublime_api.window_run_command(
                        self.window.id(),
                        'show_overlay',
                        {
                            'overlay': 'command_palette',
                            'command': self.name(),
                            'args': args
                        }
                    )
                    return
            raise

    def run(self):
        pass


class TextCommand(Command):
    def __init__(self, view):
        self.view = view

    def run_(self, edit_token, args):
        args = self.filter_args(args)
        try:
            if args:
                edit = self.view.begin_edit(edit_token, self.name(), args)
                try:
                    return self.run(edit, **args)
                finally:
                    self.view.end_edit(edit)
            else:
                edit = self.view.begin_edit(edit_token, self.name())
                try:
                    return self.run(edit)
                finally:
                    self.view.end_edit(edit)
        except (TypeError) as e:
            if 'required positional argument' in str(e):
                if sublime_api.view_can_accept_input(self.view.id(), self.name(), args):
                    sublime_api.window_run_command(
                        sublime_api.view_window(self.view.id()),
                        'show_overlay',
                        {
                            'overlay': 'command_palette',
                            'command': self.name(),
                            'args': args
                        }
                    )
                    return
            raise

    def run(self, edit):
        pass


class EventListener(object):
    pass


class ViewEventListener(object):
    @classmethod
    def is_applicable(cls, settings):
        return True

    @classmethod
    def applies_to_primary_view_only(cls):
        return True

    def __init__(self, view):
        self.view = view


class MultizipImporter(object):
    def __init__(self):
        self.loaders = []
        self.file_loaders = []

    def find_module(self, fullname, path=None):
        if not path:
            for l in self.loaders:
                if l.name == fullname:
                    return l

        for l in self.loaders:
            if path == [l.zippath]:
                if l.has(fullname):
                    return l

        return None


class ZipLoader(object):
    def __init__(self, zippath):
        self.zippath = zippath
        self.name = os.path.splitext(os.path.basename(zippath))[0]
        self._scan_zip()

    def has(self, fullname):
        name, key = fullname.split('.', 1)
        if name == self.name and key in self.contents:
            return True

        override_file = os.path.join(override_path, os.sep.join(fullname.split('.')) + '.py')
        if os.path.isfile(override_file):
            return True

        override_package = os.path.join(override_path, os.sep.join(fullname.split('.')))
        if os.path.isdir(override_package):
            return True

        return False

    def load_module(self, fullname):
        # Only if a module is being reloaded and hasn't been scanned recently
        # do we force a refresh of the contents of the .sublime-package. This
        # allows proper code upgrades using Package Control.
        if fullname in imp._RELOADING:
            if self.refreshed < time.time() - 5:
                self._scan_zip()

        source, source_path, is_pkg = self._read_source(fullname)

        if source is None:
            raise ImportError("No module named '%s'" % fullname)

        is_new = False
        if fullname in sys.modules:
            mod = sys.modules[fullname]
            old_mod_file = mod.__file__
        else:
            is_new = True
            mod = sys.modules.setdefault(fullname, imp.new_module(fullname))
            mod.__name__ = fullname
            mod.__path__ = [self.zippath]
            mod.__loader__ = self

        mod.__file__ = source_path

        if is_pkg:
            mod.__package__ = mod.__name__
        else:
            mod.__package__ = fullname.rpartition('.')[0]

        try:
            exec(compile(source, source_path, 'exec'), mod.__dict__)
            return mod

        except:
            if is_new:
                del sys.modules[fullname]
            else:
                mod.__file__ = old_mod_file
            raise

    def get_source(self, fullname):
        name, key = fullname.split('.', 1)
        if name != self.name:
            return None
        source, _, _ = self._read_source(fullname)
        return source

    def _read_source(self, fullname):
        name_parts = fullname.split('.')
        override_basename = os.path.join(override_path, *name_parts)
        override_py = override_basename + '.py'
        override_init = os.path.join(override_basename, '__init__.py')

        if os.path.isfile(override_py):
            try:
                with open(override_py, 'r', encoding='utf-8') as f:
                    return (f.read(), override_py, False)
            except (Exception) as e:
                print(override_py, 'could not be read:', e)

        if os.path.isfile(override_init):
            try:
                with open(override_init, 'r', encoding='utf-8') as f:
                    return (f.read(), override_init, True)
            except (Exception) as e:
                print(override_init, 'could not be read:', e)

        key = '.'.join(name_parts[1:])
        if key in self.contents:
            source = self.contents[key]
            source_path = os.path.join(self.zippath, self.filenames[key]).rstrip(os.sep)
            is_pkg = key in self.packages
            return (source, source_path, is_pkg)

        # This allows .py overrides to exist in subfolders that:
        #  1. Do not exist in the .sublime-package file
        #  2. Do not contain an __init__.py
        if os.path.isdir(override_basename):
            return ('', override_basename, True)

        return (None, None, False)

    def _scan_zip(self):
        self.contents = {"": ""}
        self.filenames = {"": ""}
        self.packages = {""}
        self.refreshed = time.time()

        try:
            with zipfile.ZipFile(self.zippath, 'r') as z:
                files = [i.filename for i in z.infolist()]

                for f in files:
                    base, ext = os.path.splitext(f)
                    if ext != ".py":
                        continue

                    paths = base.split('/')
                    if len(paths) > 0 and paths[len(paths) - 1] == "__init__":
                        paths.pop()
                        self.packages.add('.'.join(paths))

                    try:
                        pkg_path = '.'.join(paths)
                        self.contents[pkg_path] = z.read(f).decode('utf-8')
                        self.filenames[pkg_path] = f
                    except UnicodeDecodeError:
                        print(f, "in", self.zippath, "is not utf-8 encoded, unable to load plugin")
                        continue

                    while len(paths) > 1:
                        paths.pop()
                        parent = '.'.join(paths)
                        if parent not in self.contents:
                            self.contents[parent] = ""
                            self.filenames[parent] = parent
                            self.packages.add(parent)
        except (Exception) as e:
            print("Error loading %s:" % self.zippath, e)


override_path = None
multi_importer = MultizipImporter()
sys.meta_path.insert(0, multi_importer)


def update_compressed_packages(pkgs):
    multi_importer.loaders = []
    for p in pkgs:
        try:
            multi_importer.loaders.append(ZipLoader(p))
        except (FileNotFoundError, zipfile.BadZipFile) as e:
            print("error loading " + p + ": " + str(e))


def set_override_path(path):
    global override_path
    override_path = path
