#!/bin/bash
NEOSTATUS=$(sudo neo4j status)
if [ "$NEOSTATUS" == "Neo4j is not running" ]; then
   echo "Database is not running. Starting..."
   sudo neo4j start
   sleep 10
   bloodhound
else
   echo "Database is already started."
   bloodhound
fi
