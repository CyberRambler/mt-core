import io
import random

def is_ascii_char(s):
    """Is it an ASCII char"""
    return len(s) == 1 and '\u0000' < s[0] < '\u00ff'


def is_ascii(s):
    """All are ASCII chars"""
    return all(map(is_ascii_char, s))


EN_PUCTS = ",.?:;/<>()[]{}|\\~!@#$%^&*-+="


def is_en_punct(s):
    return len(s) == 1 and is_ascii_char(s) and EN_PUCTS.find(s)>=0


def is_zh_char(s):
    """Is it a Chinese char"""
    return len(s) == 1 and '\u4e00' <= s[0] <= '\u9fa5'


def has_zh(s):
    """Does it contain Chinese char?"""
    for c in s:
        if is_zh_char(c):
            return True
    return False


def same_lines(path1, path2):
    """Two text files have the same numbers of lines?"""
    lines1 = 0
    lines2 = 0
    with open(path1, encoding="utf-8") as f:
        for _ in f:
            lines1 += 1

    with open(path2, encoding="utf-8") as f:
        for _ in f:
            lines2 += 1

    if lines1 == lines2:
        return True
    else:
        return False


def single_to_pair(src_path, tgt_path, pair_path):
    """Combine source and target file into a parallel one"""
    assert same_lines(src_path, tgt_path)

    src_f = io.open(src_path, encoding="utf-8")
    tgt_f = io.open(tgt_path, encoding="utf-8")
    out_f = io.open(pair_path, "w", encoding="utf-8")

    cnt = 0
    for p in zip(src_f, tgt_f):
        out_f.write(p[0].strip() + "\t" + p[1].strip() + "\n")
        cnt += 1
        if cnt % 100000 == 0:
            print(cnt)
    print(cnt)
    out_f.close()


def pair_to_single(pair_path, src_path, tgt_path):
    """Split a parallel file into source ang target file"""
    src_f = io.open(src_path, "w", encoding="utf-8")
    tgt_f = io.open(tgt_path, "w", encoding="utf-8")

    tsv_f = io.open(pair_path, encoding="utf-8")
    cnt = 0
    for line in tsv_f:
        line = line.strip()
        if len(line) == 0:
            continue
        p = line.split("\t")
        if len(p) >= 2:
            src_f.write(p[0] + "\n")
            tgt_f.write(p[1] + "\n")

        cnt += 1
        if cnt % 500000 == 0:
            print(cnt)

    print(cnt)
    src_f.close()
    tgt_f.close()


def sample(files, n):
    """"Sample sentences from bitext or source and target file"""
    in_files = [io.open(f, encoding="utf-8") for f in files]
    out_files = [io.open("{}-{}".format(f, n), "w", encoding="utf-8") for f in files]

    total = count_lines(files[0])
    print(total)

    sampled = 0
    scanned = 0
    sample_prob = (1.1*n) / total
    for p in zip(*in_files):
        scanned += 1
        prob = random.uniform(0, 1)
        if prob < sample_prob:
            for i in range(len(out_files)):
                out_files[i].write(p[i].strip() + "\n")
            sampled += 1
            if sampled % 10000 == 0:
                print(scanned, sampled)
            if sampled >= n:
                break
    print(scanned, sampled)

    for f in out_files:
        f.close()


def upsample(files, n):
    """"UpSample sentences from bitext or source and target file"""
    total = count_lines(files[0])
    print(total)

    assert n>=total

    out_files = [io.open("{}-{}".format(f, n), "w", encoding="utf-8") for f in files]

    times = n // total
    sampled = 0
    for i in range(times):
        in_files = [io.open(f, encoding="utf-8") for f in files]
        for p in zip(*in_files):
            for i in range(len(out_files)):
                out_files[i].write(p[i].strip() + "\n")
                sampled += 1
                if sampled % 10000 == 0:
                    print(sampled)
        for f in in_files:
            f.close()

    scanned = 0
    sampled = 0
    n = n - total*times
    sample_prob = (1.1*n) / total
    in_files = [io.open(f, encoding="utf-8") for f in files]
    for p in zip(*in_files):
        scanned += 1
        prob = random.uniform(0, 1)
        if prob < sample_prob:
            for i in range(len(out_files)):
                out_files[i].write(p[i].strip() + "\n")
            sampled += 1
            if sampled % 10000 == 0:
                print(scanned, sampled)
            if sampled >= n:
                break
    print(scanned, sampled)

    for f in out_files:
        f.close()


def count_lines(fn):
    from tqdm import tqdm
    lines = 0
    with open(fn, encoding="utf-8") as f:
        for _ in tqdm(f):
            lines += 1

    return lines
