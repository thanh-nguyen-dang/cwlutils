from urlparse import urlparse
import os
import argparse
import subprocess
import requests
from  multiprocessing import Pool

def upload(args):
    commands = []
    pool = Pool(processes=args.processes)

    for f in args.files:
        commands.append(['aws', 's3', 'cp', f, 's3://{}/{}'.format(args.bucket, os.path.basename(f))])
    pool.map_async(run_process, commands).get(99999999)
    pool.close()
    pool.join()

def get_urls(ids, host, signpost_url):
    paths = []
    for id in ids:
        r = requests.get("{}/{}".format(signpost_url, id))
        if r.status_code == 200:
            loc = None
            for url in r.json()['urls']:
                parsed_url = urlparse(url)
                if parsed_url.scheme == 's3' and parsed_url.netloc == urlparse(host).netloc:
                    loc = parsed_url.path
                    break
            if loc:
                paths.append(loc)
            else:
                raise Exception("id {} does not have a valid url".format(id))
        else:
            raise Exception("id {} not found".format(id))
    return paths


def download(args):
    if not args.signpost_url:
        args.signpost_url = os.getenv('SIGNPOST_URL')
        if not args.signpost_url:
            print "Please provide signpost url"
            return
    paths = get_urls(args.ids, args.s3_url, args.signpost_url)
    commands = []
    pool = Pool(processes=args.processes)
    for path in paths:

        commands.append(['aws', 's3', 'cp', "s3:/{}".format(path), args.path, '--endpoint', args.s3_url])
    print commands
    pool.map_async(run_process, commands).get(99999999)
    pool.close()
    pool.join()


def run_process(commands):
    subprocess.call(commands)


def run():
    parser = argparse.ArgumentParser(description='S3 upload and download')
    parser.add_argument("--processes", type=int, default=5)
    
    parser.add_argument("--s3-url", default='https://s3.amazonaws.com')
    parser.add_argument("--access-key")
    parser.add_argument("--secret-key")

    subparsers = parser.add_subparsers(dest='command')

    download_parser = subparsers.add_parser("download")
    download_parser.add_argument("--path", default='.')
    download_parser.add_argument("ids", nargs='+', type=str)
    download_parser.add_argument("--signpost-url")

    upload_parser = subparsers.add_parser("upload")
    upload_parser.add_argument("files", nargs='+', type=str)
    upload_parser.add_argument("--bucket", required=True)

    args = parser.parse_args()
    
    if args.command == 'download':
        download(args)
    elif args.command == 'upload':
        upload(args)

if __name__ == '__main__':
    run()