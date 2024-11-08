import ipaddress
import os
import asyncio
import base64
import json
import uuid
from datetime import datetime
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的
#如果你要完我的这个TCP WS 傻子加密聊天 就开路由侠把这些端口改了 这是傻子都会的

import websockets
from websockets.exceptions import ConnectionClosedOK, ConnectionClosedError
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend

class ChatServer:
    def __init__(self, host='0.0.0.0', port=20008):
        self.host = host
        self.port = port
        self.clients = {}  # {ip: {"websocket": websocket, "session_key": session_key_bytes}}
        self.blocked_ips = set()
        self.server = None
        self.PRE_SHARED_KEY = b'G6JrXcZLw1Q8P3F7d9K0M2N4B6V8Y1A3'

        if len(self.PRE_SHARED_KEY) != 32:
            raise ValueError("预共享密钥长度不正确，应为32字节。")
        else:
            print("预共享密钥长度验证通过。")

    async def handle_client(self, websocket, path):
        user_id = str(uuid.uuid4())
        ip = websocket.remote_address[0]
        forwarded_for = websocket.request_headers.get('X-Forwarded-For')
        if forwarded_for:
            ip = forwarded_for.split(',')[0].strip()

        if not self.is_valid_ip(ip):
            print(f"无效的IP地址: {ip}")
            await websocket.close()
            return

        if ip in self.blocked_ips:
            await websocket.close()
            print(f"连接被拒绝：{ip} 已被拉黑。")
            return

        try:
            client_ip_message = await asyncio.wait_for(websocket.recv(), timeout=30)
            client_ip_data = json.loads(client_ip_message)
            if client_ip_data.get("type") == "client_ip":
                ip = client_ip_data.get("ip", ip)
        except asyncio.TimeoutError:
            print(f"客户端 {ip} 发送IP地址超时")
            await websocket.close()
            return
        except json.JSONDecodeError:
            print(f"客户端 {ip} 发送了无效的JSON数据")
            await websocket.close()
            return

        if not self.is_valid_ip(ip):
            print(f"无效的IP地址: {ip}")
            await websocket.close()
            return

        if ip in self.blocked_ips:
            await websocket.close()
            print(f"连接被拒绝：{ip} 已被拉黑。")
            return

        self.clients[ip] = {"websocket": websocket, "session_key": None}
        print(f"客户端 {ip} 已连接")

        try:
            key_exchange_request = await asyncio.wait_for(websocket.recv(), timeout=30)
            key_exchange_data = json.loads(key_exchange_request)
            if key_exchange_data.get('type') != 'request_session_key':
                print(f"未识别的密钥交换请求类型: {key_exchange_data.get('type')}")
                await websocket.close()
                return

            session_key_bytes = os.urandom(32)
            session_key_b64 = base64.b64encode(session_key_bytes).decode('utf-8')
            encrypted_session_key = self.encrypt_message(session_key_b64, self.PRE_SHARED_KEY)
            session_key_message = {
                'type': 'session_key',
                'session_key': encrypted_session_key
            }
            await websocket.send(json.dumps(session_key_message))
            print(f"已发送加密的会话密钥给 {ip}")

            self.clients[ip]["session_key"] = session_key_bytes
            await self.broadcast_system_message(f"{datetime.now().strftime('%H:%M:%S')} 系统: 欢迎 {ip}")

            await self.update_online_users()

            async for encrypted_message in websocket:
                decrypted_message = self.decrypt_message(encrypted_message, self.clients[ip]["session_key"])
                if not decrypted_message:
                    continue
                await self.handle_message(ip, decrypted_message)

        except (asyncio.TimeoutError, ConnectionClosedOK, ConnectionClosedError):
            print(f"连接超时或断开：{ip}")
        finally:
            self.remove_client(ip)
            await self.update_online_users()

    async def update_online_users(self):
        users_list = [{"ip": ip} for ip in self.clients]
        await self.broadcast({
            "type": "update_online_users",
            "users": users_list
        })

    def is_valid_ip(self, ip):
        try:
            ipaddress.ip_address(ip)
            return True
        except ValueError:
            return False

    def encrypt_message(self, message, key):
        if isinstance(message, str):
            message = message.encode('utf-8')
        iv = os.urandom(16)
        cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
        encryptor = cipher.encryptor()
        padder = padding.PKCS7(128).padder()
        padded_data = padder.update(message) + padder.finalize()
        ciphertext = encryptor.update(padded_data) + encryptor.finalize()
        iv_ciphertext = iv + ciphertext
        return base64.b64encode(iv_ciphertext).decode('utf-8')

    def decrypt_message(self, encrypted_message, key):
        try:
            iv_ciphertext = base64.b64decode(encrypted_message)
            iv = iv_ciphertext[:16]
            ciphertext = iv_ciphertext[16:]
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()
            padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()
            unpadder = padding.PKCS7(128).unpadder()
            plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
            return plaintext.decode('utf-8')
        except Exception as e:
            print(f"解密消息时出错: {e}")
            return None

    async def handle_message(self, ip, message):
        try:
            message_data = json.loads(message)
        except json.JSONDecodeError:
            print(f"消息解析失败: {message}")
            return

        msg_type = message_data.get('type')

        if msg_type == 'message':
            timestamp = datetime.now().strftime('%H:%M:%S')
            broadcast_data = {
                'type': 'message',
                'id': message_data.get('id'),
                'timestamp': timestamp,
                'username': ip,
                'content': message_data.get('content')
            }
            await self.broadcast(broadcast_data)
            print(f"{timestamp} {ip}: {message_data.get('content')}")
        elif msg_type == 'image':
            timestamp = datetime.now().strftime('%H:%M:%S')
            broadcast_data = {
                'type': 'image',
                'id': message_data.get('id'),
                'timestamp': timestamp,
                'username': ip,
                'content': message_data.get('content')
            }
            await self.broadcast(broadcast_data)
            print(f"{timestamp} {ip} 发送了一张图片。")
        elif msg_type == 'revoke':
            await self.broadcast(message_data)
            print(f"{datetime.now().strftime('%H:%M:%S')} 系统: {ip} 撤回了一条消息")

    def remove_client(self, ip):
        self.clients.pop(ip, None)
        print(f"客户端 {ip} 已断开")

    async def broadcast(self, data):
        message = json.dumps(data)
        for ip, client_info in self.clients.items():
            websocket = client_info["websocket"]
            session_key = client_info["session_key"]
            if not session_key:
                continue
            encrypted_message = self.encrypt_message(message, session_key)
            try:
                await websocket.send(encrypted_message)
            except Exception as e:
                print(f"向客户端 {ip} 发送消息出错: {e}")

    async def broadcast_system_message(self, message):
        broadcast_data = {
            'type': 'system',
            'timestamp': datetime.now().strftime('%H:%M:%S'),
            'content': message
        }
        await self.broadcast(broadcast_data)
        print(message)

    async def start_server(self):
        self.server = await websockets.serve(self.handle_client, self.host, self.port)
        print(f"服务器运行中: {self.host}:{self.port} (WS)")
        await self.server.wait_closed()

    def stop_server(self):
        if self.server:
            self.server.close()
            print(f"{datetime.now().strftime('%H:%M:%S')} 系统: 服务器已关闭")

async def main():
    server = ChatServer()
    await server.start_server()

if __name__ == "__main__":
    asyncio.run(main())
