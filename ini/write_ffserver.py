def write_line(line):
    f.write(line)
    f.write('\n')

def write_header(http_port, rtsp_port):
    write_line("# Server")
    write_line(f"HTTPPort {http_port}")
    write_line(f"RTSPPort {rtsp_port}")
    write_line("HTTPBindAddress 0.0.0.0 #set 127.0.0.1: only local can receive feed")
    write_line("MaxHTTPConnections 50 # 200")
    write_line("MaxClients 50 # 100")
    write_line("MaxBandwidth 10000000")
    write_line("CustomLog -")
    write_line("")

def write_feed(num):
    write_line("# Feed/Raw video")
    write_line(f"<Feed feed{num}.ffm>")
    write_line(f"File /tmp/feed{num}.ffm")
    write_line("FileMaxSize 8M")
    #write_line("ACL allow localhost")
    #write_line("ACL allow 127.0.0.1")
    write_line("</Feed>")
    write_line("")

def write_stream(stream_num, feed_num, stream_info):
    ext, _format, codec, pformat, size = stream_info
    write_line("# Stream")
    write_line(f"<Stream stream{stream_num}.{ext}>")
    write_line(f"Feed feed{feed_num}.ffm")
    write_line(f"Format {_format}")
    if codec:
        write_line(f"VideoCodec {codec}")
    if pformat:
        write_line(f"PixelFormat {pformat}")
    write_line("VideoBitRate    8192")
    write_line("VideoBufferSize 8192")
    write_line("VideoFrameRate  25")
    write_line("VideoQMin       2")
    write_line("VideoQMax       8")
    write_line(f"VideoSize      {size}")
    write_line("NoAudio")
    write_line("Strict          -1")
    #write_line("ACL allow 192.168.0.0 192.168.255.255")
    #write_line("ACL allow localhost")
    #write_line("ACL allow 127.0.0.1")
    write_line("</Stream>")
    write_line("")

def write_end(port):
    write_line("# Special streams")
    write_line("<Stream stat.html>")
    write_line("Format status")
    write_line("ACL allow localhost")
    write_line("ACL allow 192.168.0.0 192.168.255.255")
    write_line("</Stream>")
    write_line("")
    write_line("# Redirect index.html to the appropriate site")
    write_line("<Redirect index.html>")
    write_line("#URL http://www.graymatics.com")
    write_line(f"URL http://localhost:{port}/stat.html")
    write_line("</Redirect>")

def get_feed_total(streams):
    total = 0
    for stream in streams:
        total += stream[0]
    return total

def write_feeds(streams):
    feed_total = get_feed_total(streams)
    for i in range(feed_total):
        write_feed(i)

def write_streams(streams):
    acc_stream_count = 0
    for stream in streams:
        stream_total = stream[0]
        stream_info = stream[1:]
        for stream_i in range(stream_total):
            feed_i = stream_i + acc_stream_count
            stream_i += acc_stream_count
            write_stream(stream_i, feed_i, stream_info)
        acc_stream_count += stream_total

def write_conf():
    http_port = 8090
    rtsp_port = 8093
    streams = []
    #streams.append([80, 'sdp', 'rtp', 'libx264', 'yuv420p', '640x480'])
    #streams.append([80, 'mjpeg', 'rtp', '', '', '640x480'])
    streams.append([30, 'mjpeg', 'mpjpeg', '', '', '640x480'])
    write_header(http_port, rtsp_port)
    write_feeds(streams)
    write_streams(streams)
    write_end(http_port)


if __name__ == '__main__':
    filename = 'server.conf'
    f = open(filename, 'w')

    write_conf()
    f.close()
