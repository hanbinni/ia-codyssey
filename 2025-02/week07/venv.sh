#!/bin/bash
# venv 가상환경 토글 스크립트

if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "가상환경이 활성화되어 있습니다. 비활성화합니다."
    deactivate
else
    echo "가상환경이 활성화되어 있지 않습니다. 활성화합니다."
    source .venv/bin/activate
fi