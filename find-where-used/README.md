# DataStage Impact Analyzer

## Overview
DataStage Impact Analyzer is a lightweight utility that helps data engineering teams
identify DataStage objects impacted by a given table name, file name, or search string.

In large IBM DataStage environments, impact analysis is often manual and time-consuming.
This tool automates that process by scanning exported DataStage DSX files and returning
a list of objects where the search string is referenced.

## Problem Statement
Enterprise ETL platforms such as IBM DataStage typically contain hundreds or thousands
of jobs, parameter sets, etc.

When a schema, table, or file changes, teams must answer a common question:
> “Which DataStage objects are impacted by this change?”

Native tooling and documentation are often insufficient, leading to:
- Manual code searches
- Missed dependencies
- Increased risk during production changes

## Solution
This project provides a simple, script-based approach to impact analysis by:
- Scanning exported DataStage DSX files
- Searching object definitions for a given string
- Returning a unique list of impacted object names

The tool is intentionally minimal and easy to understand, mirroring how impact analysis
is typically performed in real enterprise environments.

## How It Works
1. A DataStage project (or selected components) is exported as a DSX file, WITHOUT executables
2. The script scans each object definition within the DSX - case insensitive search
3. If the search string is found within an object, the object name is recorded
4. Results are written to a timestamped output file for easy reference

The script supports nested DSX structures, including:
- Jobs
- Parameter sets
- Routines (not fully tested)

## Usage
python ds_impact_analyzer.py <dsx_file> <search_string>

## Usage
python ds_impact_analyzer.py project_export.dsx CUSTOMER_TABLE

This will generate an output file in the same directory as the script.
ds_job_list_CUSTOMER_TABLE.txt


## Output Format
Datetime: 2026-02-10 15:01:33
Search string = CUSTOMER_TABLE
Input file: project_export.dsx
Total match count: 4
------------------------
Below is the list of objects where the search string was found

1. object name: LOAD_CUSTOMER_DIM
2. object name: UPDATE_CUSTOMER_FACT
3. object name: PS_CUSTOMER_TABLES
4. object name: ROUTINE_SQL_HELPER