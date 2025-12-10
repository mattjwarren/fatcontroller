from fabric import Connection, Config
import sys
import logging

# Configure logging to match app
logging.basicConfig(level=logging.DEBUG)

def test_connection():
    target = "192.168.1.101"
    user = "matt"
    password = "matt"
    
    print(f"Testing connection to {user}@{target} with NumberOfPasswordPrompts='0'...")
    
    connect_kwargs = {}
    connect_kwargs['timeout'] = 10
    connect_kwargs['banner_timeout'] = 10
    connect_kwargs['look_for_keys'] = False
    connect_kwargs['password'] = password
    
    # Exact config from FC_SSH.py including the prompt setting
    config = Config(overrides={
        'run': {'warn': True}, 
        'ssh_config': {
            'StrictHostKeyChecking': 'no',
            'NumberOfPasswordPrompts': '0'
        }
    })
    
    conn = Connection(
        host=target,
        user=user,
        config=config,
        connect_kwargs=connect_kwargs
    )
    
    try:
        print("Attempting to open connection...")
        conn.open()
        print("Connection opened successfully!")
        
        print("Running 'ls' command...")
        result = conn.run("ls", hide=True, warn=True)
        print("Command executed.")
        if result.stdout:
            print("STDOUT:", result.stdout)
            
        conn.close()
        print("Test Passed.")
        
    except Exception as e:
        print(f"Test Failed: {e}")
        # sys.exit(1)

if __name__ == "__main__":
    test_connection()
