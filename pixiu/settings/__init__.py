import os

env_name = 'PIXIU_ENV'
_env = os.getenv(env_name, None)
print(f'Detected {env_name}: {_env}')

try:
    if _env == 'dev':
        from .dev import *
    elif _env == 'prod':
        from .prod import *
    else:
        import platform

        if 'darwin' in platform.platform().lower() or 'windows' in platform.platform().lower():
            _env = 'dev'
            print(f'检测到{platform.system()}平台，自动切换到dev环境')
            from .dev import *
        else:
            print('获取环境变量失败，加载基础配置')
            from .base import *
except ImportError as e:
    import sys

    print(f'加载配置文件settings/{_env}.py失败，{e}，请检查{env_name}环境变量和配置文件是否正常！')
    sys.exit(1)
