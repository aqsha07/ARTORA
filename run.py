import os
from app import create_app

app = create_app(os.getenv('FLASK_ENV', 'development'))

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('FLASK_DEBUG', 'True').lower() in ('true', '1', 't')
    print(f"==================================================")
    print(f"  ARTORA - Create Without Limits.")
    print(f"  Online Art Supplies & Essentials Store")
    print(f"  Running on: http://127.0.0.1:{port}")
    print(f"==================================================")
    app.run(host='0.0.0.0', port=port, debug=debug)
