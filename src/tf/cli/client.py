
import sys
import os

#ZIP_PATH = '/Users/mikeh/home/projects/classes/INFO490Assets/src'

#parent = os.path.abspath(os.path.dirname(__file__))
parent = os.path.abspath('..')
ZIP_PATH = os.path.dirname(parent)
if ZIP_PATH not in sys.path:
    sys.path.append(ZIP_PATH)

from tf.utils import ZipLib  # if error make sure python3 is running
from tf.utils import Client
from tf.utils import SandBox
from tf.utils import GradescopeResultParser as GRP

'''
 To test an assignment: assn1/solution.py
  test a single file
      python client.py assn1/solution.py
      python client.py solution.py (inside assn1)
  test a directory
      python client.py assn1/
      python client.py . (inside assn1)
'''

server = 'http://0.0.0.0:5000'
server = 'localhost:8080'
server = 'http://192.168.1.78:8080'  # laptop localhost

server = 'http://ec2-18-219-123-225.us-east-2.compute.amazonaws.com:8080'
server = 'http://127.0.0.1:8080'


# python3 client.py --tag INFO:PPM --input test --fn worst_zip

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description='Test python')
    parser.add_argument('--tag',   type=str, help='assignment tag', default='01', required=False)
    parser.add_argument('--input', type=str, help='test file or directory')
    parser.add_argument('--fn',    type=str, help='test function', required=False, default=None)
    args = parser.parse_args()

    assignment_dir = args.input
    assignment_tag = args.tag
    fn_name        = args.fn

    client = Client.ClientTest(assignment_tag, server=server)

    print("TESTING server", server)
    print("TESTING function", fn_name)

    sandbox = SandBox.SandBox()
    zip_file = ZipLib.create_zipfile(assignment_dir,  sandbox.get_sandbox_dir())
    print('created', zip_file)

    kv = {"fn": fn_name}
    response = client.send_zip(zip_file, kv)
    #print(response)

    error   = response['error_code']
    payload = response['payload']
    fp = "{:s}/{:s}".format(sandbox.get_sandbox_dir(), "results.json")
    if error is None:
        print(payload['test_result'])
        GRP.do_matplot(payload['test_result'])

        import json
        with open(fp, 'w') as fd:
            pp = json.dumps(payload['test_result'], indent=4)
            fd.write(pp)

    else:
        print('ERROR', error)
        print(payload)


