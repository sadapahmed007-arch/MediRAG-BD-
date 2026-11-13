"""MediRAG-BD: Start the complete application (backend + frontend)."""
import subprocess
import sys
import os
import time
import signal

def main():
    base = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(base)

    print("=" * 60)
    print("  MediRAG-BD: Starting Application")
    print("=" * 60)

    # Check models exist
    models_dir = os.path.join(base, 'models')
    required = ['intent_model.pkl', 'topic_model.pkl', 'safety_model.pkl']
    missing = [f for f in required if not os.path.exists(os.path.join(models_dir, f))]
    if missing:
        print(f"ERROR: Missing models: {missing}")
        print("Run: python scripts/complete_build.py")
        sys.exit(1)

    indexes_dir = os.path.join(base, 'data', 'indexes')
    if not os.path.exists(os.path.join(indexes_dir, 'faiss_index.bin')):
        print("ERROR: FAISS index not found.")
        print("Run: python scripts/complete_build.py")
        sys.exit(1)

    print("\n[1/2] Starting FastAPI backend on port 8000...")
    backend = subprocess.Popen(
        [sys.executable, '-m', 'uvicorn', 'app.backend.main:app',
         '--host', '0.0.0.0', '--port', '8000'],
        cwd=base,
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding='utf-8', errors='replace',
    )

    # Wait for backend to start
    time.sleep(5)

    print("[2/2] Starting React frontend on port 3000...")
    frontend = subprocess.Popen(
        ['npm', 'run', 'dev'],
        cwd=os.path.join(base, 'app', 'frontend'),
        stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, encoding='utf-8', errors='replace',
        shell=True,
    )

    print("\n" + "=" * 60)
    print("  MediRAG-BD is running!")
    print("  Frontend: http://localhost:3000")
    print("  Backend:  http://localhost:8000")
    print("  API Docs: http://localhost:8000/docs")
    print("  Press Ctrl+C to stop")
    print("=" * 60)

    try:
        while True:
            # Print backend output
            line = backend.stdout.readline()
            if line:
                print(f"[backend] {line.rstrip()}")
            if backend.poll() is not None:
                print("Backend stopped!")
                break
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        backend.terminate()
        frontend.terminate()
        print("Stopped.")


if __name__ == '__main__':
    main()
