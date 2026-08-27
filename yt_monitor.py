#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
yt_monitor.py - Theo doi suc khoe SEO cua nhieu kenh YouTube cung luc.

Chi can YouTube Data API v3 + API key (KHONG can OAuth, khong can cai thu vien).
Moi lan chay se luu 1 snapshot vao data/ va tu so sanh voi lan chay truoc.
"""

import csv
import json
import os
import re
import statistics
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

BASE = "https://www.googleapis.com/youtube/v3"
ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(ROOT, "data")
CHANNELS_FILE = os.path.join(ROOT, "channels.txt")

LOOKBACK_N = 20   # lay 20 video gan nhat moi kenh
RECENT_N = 10     # 10 video moi nhat = "hien tai", 10 video ke tiep = "truoc do"
SHORTS_MAX_SEC = 60


# ----------------------------------------------------------------- tien ich

def die(msg):
    print("\n[LOI] " + msg + "\n")
    sys.exit(1)


def get_api_key():
    key = os.environ.get("YOUTUBE_API_KEY", "").strip()
    if key:
        return key
    path = os.path.join(ROOT, "api_key.txt")
    if os.path.exists(path):
        with open(path, encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith("#"):
                    return line
    die("Chua co API key. Tao file api_key.txt trong thu muc nay va dan key vao.\n"
        "       Huong dan lay key: xem README.md muc 1.")


def api_get(endpoint, params, key):
    params = dict(params)
    params["key"] = key
    url = BASE + "/" + endpoint + "?" + urllib.parse.urlencode(params)
    req = urllib.request.Request(url, headers={"Accept": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raw = e.read().decode("utf-8", "replace")
        reason, message = "", raw[:300]
        try:
            err = json.loads(raw)["error"]
            message = err.get("message", message)
            if err.get("errors"):
                reason = err["errors"][0].get("reason", "")
        except Exception:
            pass
        if reason == "quotaExceeded":
            die("Het quota API cho hom nay (moi project duoc 10.000 units/ngay).\n"
                "       Doi sang ngay mai hoac xin tang quota trong Google Cloud Console.")
        if reason in ("keyInvalid", "badRequest", "forbidden"):
            die("API key khong hop le hoac chua bat YouTube Data API v3.\n"
                "       Chi tiet: " + message)
        die("Goi API that bai (%s %s): %s" % (e.code, reason, message))
    except urllib.error.URLError as e:
        die("Khong ket noi duoc toi Google API: %s" % e.reason)


def chunks(seq, n):
    for i in range(0, len(seq), n):
        yield seq[i:i + n]


def parse_duration(iso):
    """PT1H2M3S -> so giay."""
    m = re.match(r"^P(?:(\d+)D)?T(?:(\d+)H)?(?:(\d+)M)?(?:(\d+)S)?$", iso or "")
    if not m:
        return 0
    d, h, mi, s = (int(x) if x else 0 for x in m.groups())
    return d * 86400 + h * 3600 + mi * 60 + s


def days_since(iso_ts):
    for pattern in ("%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ"):
        try:
            dt = datetime.strptime(iso_ts, pattern).replace(tzinfo=timezone.utc)
        except (ValueError, TypeError):
            continue
        return max((datetime.now(timezone.utc) - dt).total_seconds() / 86400.0, 0.01)
    return None


def fmt(n):
    """1234567 -> 1.234.567 (kieu VN)."""
    try:
        return "{:,}".format(int(n)).replace(",", ".")
    except (TypeError, ValueError):
        return "-"


def pct(new, old):
    if not old:
        return None
    return (new - old) / float(old) * 100.0


# ------------------------------------------------------- doc & nhan dien kenh

def read_channel_entries():
    if not os.path.exists(CHANNELS_FILE):
        die("Khong thay file channels.txt. Moi dong 1 kenh (link, @handle hoac UC...).")
    out = []
    with open(CHANNELS_FILE, encoding="utf-8") as f:
        for line in f:
            line = line.split("#")[0].strip()
            if line:
                out.append(line)
    if not out:
        die("channels.txt dang rong. Them cac kenh can theo doi vao day.")
    return out


def classify(raw):
    """Tra ve ('id'|'handle'|'username', gia_tri)."""
    s = raw.strip()
    if s.startswith("http"):
        parts = [p for p in urllib.parse.urlparse(s).path.strip("/").split("/") if p]
        if not parts:
            return ("handle", s)
        if parts[0] == "channel" and len(parts) > 1:
            return ("id", parts[1])
        if parts[0] == "user" and len(parts) > 1:
            return ("username", parts[1])
        s = parts[1] if parts[0] == "c" and len(parts) > 1 else parts[0]
    if re.match(r"^UC[A-Za-z0-9_-]{22}$", s):
        return ("id", s)
    if s.startswith("@"):
        return ("handle", s)
    return ("handle", "@" + s)


def resolve_ids(entries, key):
    """Doi moi dong trong channels.txt thanh channelId."""
    resolved, failed = [], []
    for raw in entries:
        kind, val = classify(raw)
        if kind == "id":
            resolved.append(val)
            continue
        param = "forHandle" if kind == "handle" else "forUsername"
        data = api_get("channels", {"part": "id", param: val}, key)
        items = data.get("items") or []
        if items:
            resolved.append(items[0]["id"])
        else:
            failed.append(raw)
    return resolved, failed


# ------------------------------------------------------------- lay du lieu

def fetch_channels(ids, key):
    out = []
    for group in chunks(ids, 50):
        data = api_get("channels", {
            "part": "snippet,statistics,contentDetails",
            "id": ",".join(group),
            "maxResults": 50,
        }, key)
        out.extend(data.get("items") or [])
    return out


def fetch_recent_video_ids(uploads_playlist, key):
    data = api_get("playlistItems", {
        "part": "contentDetails",
        "playlistId": uploads_playlist,
        "maxResults": LOOKBACK_N,
    }, key)
    items = data.get("items") or []
    return [it["contentDetails"]["videoId"] for it in items]


def fetch_videos(video_ids, key):
    out = {}
    for group in chunks(video_ids, 50):
        data = api_get("videos", {
            "part": "snippet,statistics,contentDetails",
            "id": ",".join(group),
            "maxResults": 50,
        }, key)
        for it in data.get("items") or []:
            out[it["id"]] = it
    return out


# --------------------------------------------------------------- tinh toan

def build_row(ch, videos):
    """videos: list chi tiet video, thu tu moi -> cu."""
    snip = ch["snippet"]
    stats = ch.get("statistics", {})

    def views_of(v):
        return int(v.get("statistics", {}).get("viewCount", 0) or 0)

    longform, shorts = [], []
    for v in videos:
        sec = parse_duration(v.get("contentDetails", {}).get("duration"))
        if sec <= SHORTS_MAX_SEC:
            shorts.append(v)
        else:
            longform.append(v)

    lf_views = [views_of(v) for v in longform]
    recent_lf = lf_views[:RECENT_N]
    prior_lf = lf_views[RECENT_N:RECENT_N * 2]

    med_recent = statistics.median(recent_lf) if recent_lf else 0
    med_prior = statistics.median(prior_lf) if prior_lf else 0
    trend = pct(med_recent, med_prior)

    # nhip dang bai: so ngay trung binh giua cac video gan nhat
    ages = [days_since(v["snippet"]["publishedAt"]) for v in videos]
    ages = [a for a in ages if a is not None]
    cadence = (max(ages) - min(ages)) / (len(ages) - 1) if len(ages) > 1 else None
    last_upload = min(ages) if ages else None

    # toc do keo view cua video moi (view/ngay) - tin hieu SEO ro nhat
    velocity = []
    for v in longform[:RECENT_N]:
        a = days_since(v["snippet"]["publishedAt"])
        if a and a >= 1:
            velocity.append(views_of(v) / a)
    avg_velocity = statistics.mean(velocity) if velocity else 0

    # ve sinh SEO tren metadata cua cac video moi
    counts = {"title_dai": 0, "mo_ta_ngan": 0, "thieu_tag": 0}
    checked = videos[:RECENT_N]
    for v in checked:
        s = v["snippet"]
        if len(s.get("title", "")) > 70:
            counts["title_dai"] += 1
        if len(s.get("description", "")) < 200:
            counts["mo_ta_ngan"] += 1
        if not s.get("tags"):
            counts["thieu_tag"] += 1

    top = max(longform, key=views_of) if longform else None

    return {
        "channel_id": ch["id"],
        "ten_kenh": snip.get("title", ""),
        "subs": int(stats.get("subscriberCount", 0) or 0),
        "tong_view": int(stats.get("viewCount", 0) or 0),
        "tong_video": int(stats.get("videoCount", 0) or 0),
        "median_view_10_moi": int(med_recent),
        "median_view_10_truoc": int(med_prior),
        "xu_huong_pct": round(trend, 1) if trend is not None else "",
        "view_moi_ngay": int(avg_velocity),
        "nhip_dang_ngay": round(cadence, 1) if cadence else "",
        "ngay_tu_video_cuoi": int(last_upload) if last_upload is not None else "",
        "so_video_kiem_tra": len(checked),
        "so_shorts_trong_20": len(shorts),
        "loi_title_dai": counts["title_dai"],
        "loi_mo_ta_ngan": counts["mo_ta_ngan"],
        "loi_thieu_tag": counts["thieu_tag"],
        "video_top": top["snippet"]["title"][:80] if top else "",
        "view_video_top": views_of(top) if top else 0,
    }


# -------------------------------------------------------------- snapshot

def latest_snapshot():
    if not os.path.isdir(DATA_DIR):
        return None
    files = sorted(f for f in os.listdir(DATA_DIR)
                   if f.startswith("snapshot_") and f.endswith(".csv"))
    if not files:
        return None
    path = os.path.join(DATA_DIR, files[-1])
    with open(path, encoding="utf-8-sig", newline="") as f:
        rows = {}
        for r in csv.DictReader(f):
            rows[r["channel_id"]] = r
    return files[-1], rows


def save_snapshot(rows):
    if not os.path.isdir(DATA_DIR):
        os.makedirs(DATA_DIR)
    name = "snapshot_%s.csv" % datetime.now().strftime("%Y-%m-%d")
    path = os.path.join(DATA_DIR, name)
    with open(path, "w", encoding="utf-8-sig", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    return path


# ----------------------------------------------------------------- hien thi

def report(rows, previous):
    prev_name, prev_rows = previous if previous else (None, {})
    rows = sorted(rows, key=lambda r: r["view_moi_ngay"], reverse=True)

    print("")
    print("=" * 98)
    print("BAO CAO %d KENH  -  %s" % (len(rows), datetime.now().strftime("%d/%m/%Y %H:%M")))
    if prev_name:
        print("So sanh voi lan chay truoc: %s" % prev_name)
    print("=" * 98)
    print("")
    print("%-24s %10s %9s %12s %9s %11s %8s" % (
        "KENH", "SUBS", "SUB +/-", "MEDIAN 10", "XU HUONG", "VIEW/NGAY", "IM LANG"))
    print("-" * 98)

    for r in rows:
        sub_delta = ""
        p = prev_rows.get(r["channel_id"])
        if p:
            try:
                sub_delta = "%+d" % (r["subs"] - int(p["subs"]))
            except (ValueError, KeyError, TypeError):
                sub_delta = ""
        trend = r["xu_huong_pct"]
        trend_s = ("%+.0f%%" % trend) if trend != "" else "n/a"
        silence = r["ngay_tu_video_cuoi"]
        silence_s = ("%dd" % silence) if silence != "" else "-"
        print("%-24s %10s %9s %12s %9s %11s %8s" % (
            r["ten_kenh"][:24],
            fmt(r["subs"]),
            sub_delta,
            fmt(r["median_view_10_moi"]),
            trend_s,
            fmt(r["view_moi_ngay"]),
            silence_s,
        ))

    print("")
    print("-" * 98)
    print("CAN CHU Y")
    print("-" * 98)
    alerts = 0
    for r in rows:
        msgs = []
        t = r["xu_huong_pct"]
        if t != "" and t <= -30:
            msgs.append("10 video moi tut %.0f%% view so voi 10 video truoc do" % t)
        if r["ngay_tu_video_cuoi"] != "" and r["ngay_tu_video_cuoi"] > 21:
            msgs.append("khong dang bai %d ngay" % r["ngay_tu_video_cuoi"])
        n = r["so_video_kiem_tra"]
        if n and r["loi_thieu_tag"] >= n * 0.5:
            msgs.append("%d/%d video moi khong co tag" % (r["loi_thieu_tag"], n))
        if n and r["loi_mo_ta_ngan"] >= n * 0.5:
            msgs.append("%d/%d video mo ta duoi 200 ky tu" % (r["loi_mo_ta_ngan"], n))
        if n and r["loi_title_dai"] >= n * 0.5:
            msgs.append("%d/%d video title dai qua 70 ky tu (bi cat tren ket qua tim kiem)"
                        % (r["loi_title_dai"], n))
        if msgs:
            alerts += 1
            print("  * " + r["ten_kenh"][:50])
            for m in msgs:
                print("      - " + m)
    if alerts == 0:
        print("  Khong co canh bao nao.")
    print("")


# --------------------------------------------------------------------- main

def main():
    key = get_api_key()
    entries = read_channel_entries()
    print("Doc %d kenh tu channels.txt ..." % len(entries))

    ids, failed = resolve_ids(entries, key)
    for f in failed:
        print("  [bo qua] khong tim thay kenh: %s" % f)
    if not ids:
        die("Khong nhan dien duoc kenh nao. Kiem tra lai channels.txt.")

    channels = fetch_channels(ids, key)
    print("Lay duoc %d kenh. Dang tai video gan nhat ..." % len(channels))

    per_channel_ids = {}
    all_video_ids = []
    for ch in channels:
        pl = ch.get("contentDetails", {}).get("relatedPlaylists", {}).get("uploads")
        vids = fetch_recent_video_ids(pl, key) if pl else []
        per_channel_ids[ch["id"]] = vids
        all_video_ids.extend(vids)

    details = fetch_videos(all_video_ids, key)
    print("Phan tich %d video ..." % len(details))

    rows = []
    for ch in channels:
        vids = [details[v] for v in per_channel_ids[ch["id"]] if v in details]
        rows.append(build_row(ch, vids))

    previous = latest_snapshot()
    report(rows, previous)
    path = save_snapshot(rows)
    print("Da luu snapshot: %s" % path)
    print("Mo file do bang Excel de xem day du cac cot.")
    print("")


if __name__ == "__main__":
    main()
