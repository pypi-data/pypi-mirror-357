#!/usr/bin/env python3

import argparse, importlib, svllm, uvicorn
from termcolor import colored

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--chat', type=str, required=False, help='chat function')
    parser.add_argument('--complete', type=str, required=False, help='complete function')
    parser.add_argument('--embed', type=str, required=False, help='embed function')

    parser.add_argument('--prefix', type=str, default='/v1', required=False, help='api prefix')
    parser.add_argument('--host', type=str, default='127.0.0.1', required=False, help='host address')
    parser.add_argument('--port', type=int, default=5261, required=False, help='port number')
    parser.add_argument('--quiet', action='store_true', help='suppress output')

    cmd_args = parser.parse_args()

    def log(message: str, error = False):
        if not cmd_args.quiet:
            color: str = 'red' if error else 'green'
            print(colored('svllm:', color) + f'     {message}')

    if cmd_args.chat:
        segments = cmd_args.chat.split(':')
        path = segments[0]
        func = segments[1] if len(segments) > 1 else 'chat'
        chat = getattr(importlib.import_module(path), func)
        if not chat:
            raise ImportError(f'Chat function \'{func}\' not found in module \'{path}\'')
        svllm.base.set_chat(chat)
        log(f'Chat function set to ' + colored(f'{path}:{func}', 'yellow'))

    if cmd_args.complete:
        segments = cmd_args.complete.split(':')
        path = segments[0]
        func = segments[1] if len(segments) > 1 else 'complete'
        complete = getattr(importlib.import_module(path), func)
        if not complete:
            raise ImportError(f'Complete function \'{func}\' not found in module \'{path}\'')
        svllm.base.set_complete(complete)
        log(f'Complete function set to ' + colored(f'{path}:{func}', 'yellow'))

    if cmd_args.embed:
        segments = cmd_args.embed.split(':')
        path = segments[0]
        func = segments[1] if len(segments) > 1 else 'embed'
        embed = getattr(importlib.import_module(path), func)
        if not embed:
            raise ImportError(f'Embed function \'{func}\' not found in module \'{path}\'')
        svllm.base.set_embed(embed)
        log(f'Embed function set to ' + colored(f'{path}:{func}', 'yellow'))

    log_level = 'warning' if cmd_args.quiet else 'info'
    app = svllm.create_app(title='svllm API', description='svllm API', prefix=cmd_args.prefix)
    uvicorn.run(app, host=cmd_args.host, port=cmd_args.port, log_level=log_level)

if __name__ == "__main__":
    main()
