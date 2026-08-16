import zlib, struct, math

def png(path, w, h, px):
    raw = b''.join(b'\x00' + bytes(px[y*w*4:(y+1)*w*4]) for y in range(h))
    def chunk(t, d):
        c = struct.pack('>I', len(d)) + t + d
        return c + struct.pack('>I', zlib.crc32(t+d) & 0xffffffff)
    out = (b'\x89PNG\r\n\x1a\n'
           + chunk(b'IHDR', struct.pack('>IIBBBBB', w, h, 8, 6, 0, 0, 0))
           + chunk(b'IDAT', zlib.compress(raw, 9))
           + chunk(b'IEND', b''))
    open(path, 'wb').write(out)

SS = 3  # supersample factor

def draw(size):
    N = size * SS
    acc = [[0.0]*4 for _ in range(N*N)]
    cx, cy = N*0.5, N*0.62      # apex of the antenna / wave origin
    for y in range(N):
        for x in range(N):
            # background vertical gradient: deep navy -> lighter blue
            t = y / (N-1)
            r, g, b = 10 + 12*t, 22 + 34*t, 45 + 70*t
            a = 255.0
            dx, dy = x - cx, y - cy
            d = math.hypot(dx, dy)
            ang = math.atan2(-dy, dx)      # up is positive
            # three concentric wave arcs above the apex, ~110 deg spread
            if math.pi*0.19 < ang < math.pi*0.81:
                for i, rad in enumerate((0.20, 0.31, 0.42)):
                    R = rad * N
                    thick = N * 0.030
                    if abs(d - R) < thick:
                        f = 1.0 - abs(d - R)/thick
                        f = min(1.0, f*1.7)
                        r += (255-r)*f; g += (255-g)*f; b += (255-b)*f
            # vertical mast
            mw = N*0.021
            if abs(dx) < mw and 0 <= dy < N*0.30:
                r = g = b = 255.0
            # base bar
            if abs(dy - N*0.30) < N*0.021 and abs(dx) < N*0.115:
                r = g = b = 255.0
            acc[y*N+x] = [r, g, b, a]
    # downsample
    px = bytearray(size*size*4)
    for y in range(size):
        for x in range(size):
            s = [0.0]*4
            for j in range(SS):
                for i in range(SS):
                    p = acc[(y*SS+j)*N + (x*SS+i)]
                    for k in range(4): s[k] += p[k]
            o = (y*size+x)*4
            for k in range(4):
                px[o+k] = max(0, min(255, int(s[k]/(SS*SS) + 0.5)))
    return px

for s in (180, 192, 512, 1024):
    png(f'app/icons/icon-{s}.png', s, s, draw(s))
    print('wrote icon-%d.png' % s)
