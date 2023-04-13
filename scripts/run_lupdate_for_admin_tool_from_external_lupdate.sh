#!/bin/bash

cd ../utils/external/lupdate
lupdate "../../admin_tool/game-chat-admin-tool/game-chat-admin-tool.pro"
$SHELL


# !!! This script relies on the fact that utils/external/lupdate folder has lupdate.exe executable (in a working state)
