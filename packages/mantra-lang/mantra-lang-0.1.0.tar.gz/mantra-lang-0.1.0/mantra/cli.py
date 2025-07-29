#!/usr/bin/env python3
"""
Mantra Programming Language CLI
"""

import sys
import os
import argparse

def main():
    # Debug: Print that we're starting
    # print("DEBUG: CLI starting...")
    
    parser = argparse.ArgumentParser(
        description='Mantra Programming Language - Sanskrit-inspired coding',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  mantra hello.man           # Run a Mantra file
  mantra --repl             # Start interactive REPL  
  mantra --version          # Show version
  
Visit https://github.com/mantra-lang/mantra for documentation.
        '''
    )
    
    parser.add_argument('file', nargs='?', help='Mantra source file (.man)')
    parser.add_argument('--version', action='version', version='Mantra 0.1.0')
    parser.add_argument('--repl', '-r', action='store_true', help='Start interactive REPL')
    parser.add_argument('--debug', '-d', action='store_true', help='Enable debug mode')
    
    try:
        args = parser.parse_args()
    except SystemExit as e:
        # --version was used, which causes sys.exit()
        sys.exit(e.code)
    
    # Import here to avoid circular imports
    try:
        from . import MantraRunner
    except ImportError:
        # If relative import fails, try absolute import
        try:
            from mantra import MantraRunner
        except ImportError:
            print("Error: Cannot import MantraRunner. Check your installation.")
            sys.exit(1)
    
    # Create runner instance
    try:
        runner = MantraRunner()
    except Exception as e:
        print(f"Error creating MantraRunner: {e}")
        sys.exit(1)
    
    # Handle REPL mode
    if args.repl or not args.file:
        try:
            runner.repl()
        except Exception as e:
            print(f"Error in REPL: {e}")
            if args.debug:
                import traceback
                traceback.print_exc()
            sys.exit(1)
    else:
        # Handle file execution
        if not args.file.endswith('.man'):
            print("Error: Mantra files must have .man extension")
            print("Example: mantra hello.man")
            sys.exit(1)
        
        if not os.path.exists(args.file):
            print(f"Error: File '{args.file}' not found")
            sys.exit(1)
        
        try:
            result = runner.run_file(args.file)
            if result is None and args.debug:
                print("DEBUG: run_file returned None")
        except Exception as e:
            print(f"Error running file: {e}")
            if args.debug:
                import traceback
                traceback.print_exc()
            sys.exit(1)

if __name__ == "__main__":
    main()