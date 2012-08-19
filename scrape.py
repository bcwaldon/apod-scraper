import progressbar
import os.path
import sys
import httplib


def http_request(uri):
    http = httplib.HTTPConnection('apod.nasa.gov')
    http.request('GET', uri)
    return http.getresponse()


def parse_link(link):
    link = link[link.find("\"")+1:]
    return link[:link.find("\"")]

def download(uri, outdir):
    index = http_request(uri).read()
    lines = index.split('\n')
    for line in lines:
        if line.startswith('<a') and 'image/' in line:
            img_line = line
            break
    else:
        img_line = None

    prev_line = None
    for line in lines:
        if line.startswith('<a') and '&lt;' in line:
            prev_line = line
            break

    if prev_line is not None:
        prev_link = parse_link(prev_line)
    else:
        prev_link = None


    if img_line is None:
        print 'Could not parse image link!'
    else:
        img_link = parse_link(img_line)

        img_name = img_link.rsplit('/', 1)[1]
        outfile = '%s/%s' % (outdir, img_name)
        if os.path.exists(outfile):
            print 'Skipping %s - already exists.' % img_name
        else:
            print 'Downloading %s' % img_name
            img_data = http_request('/%s' % img_link)

            content_length = int(img_data.getheader('content-length'))
            progress = progressbar.ProgressBar(maxval=content_length).start()

            def read():
                chunk = img_data.read(65536)
                progress.update(progress.currval+len(chunk))
                return chunk

            with open(outfile, 'w') as fap:
                data = read()

                while data:
                    fap.write(data)
                    data = read()

            progress.finish()

    return prev_link


if __name__=='__main__':
    outdir = sys.argv[1]
    prev_link = download('/apod/astropix.html', outdir)
    while prev_link:
        prev_link = download('/apod/%s' % prev_link, outdir)
