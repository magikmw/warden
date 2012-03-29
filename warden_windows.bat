@echo off
IF EXISTS warden.log MOVE warden.log warden.log_old
start /B ".\main\__main__.exe"
