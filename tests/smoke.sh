#!/usr/bin/env bash
# Live smoke test for https://knowwhatiown.com. Read-only; safe to run any time.
# Usage: tests/smoke.sh [base_url]     (default https://knowwhatiown.com)
set -u
BASE="${1:-https://knowwhatiown.com}"
HOST="${BASE#https://}"; HOST="${HOST%%/*}"
fails=0
pass() { echo "ok    $1"; }
fail() { echo "FAIL  $1"; fails=$((fails+1)); }
code() { curl -s -o /dev/null -w '%{http_code}' --max-time 20 "$1"; }

# 1. required pages return 200 over HTTPS
for p in "/" "/support.html" "/privacy.html" "/robots.txt" "/sitemap.xml" "/assets/styles.css"; do
  c=$(code "$BASE$p"); [ "$c" = "200" ] && pass "200 $p" || fail "$p returned $c"
done

# 2. unknown paths 404 (and serve the branded page)
not_found=$(curl -s --max-time 20 "$BASE/definitely-not-a-page")
c=$(code "$BASE/definitely-not-a-page"); [ "$c" = "404" ] && pass "404 for unknown path" || fail "unknown path returned $c"
echo "$not_found" | grep -q 'Page not found' && pass "404 serves branded recovery page" || fail "404 missing branded recovery page"

# 3. HTTP redirects to HTTPS (only meaningful for the real domain)
if [ "$HOST" = "knowwhatiown.com" ]; then
  headers=$(curl -sI --max-time 20 "http://$HOST/")
  code_http=$(printf '%s\n' "$headers" | head -n 1 | awk '{print $2}')
  loc=$(printf '%s\n' "$headers" | tr -d '\r' | awk -F': ' 'tolower($1)=="location"{print $2; exit}')
  [ "$code_http" = "301" ] || [ "$code_http" = "308" ] && pass "http uses a permanent redirect" || fail "http redirect status was $code_http"
  case "$loc" in https://knowwhatiown.com/*|https://knowwhatiown.com) pass "http redirects to canonical https apex";; *) fail "http canonical redirect is $loc";; esac
  headers=$(curl -sI --max-time 20 "https://www.$HOST/")
  code_www=$(printf '%s\n' "$headers" | head -n 1 | awk '{print $2}')
  loc=$(printf '%s\n' "$headers" | tr -d '\r' | awk -F': ' 'tolower($1)=="location"{print $2; exit}')
  [ "$code_www" = "301" ] || [ "$code_www" = "308" ] && pass "www uses a permanent redirect" || fail "www redirect status was $code_www"
  case "$loc" in https://knowwhatiown.com/*|https://knowwhatiown.com) pass "www redirects to canonical apex";; *) fail "www canonical redirect is $loc";; esac
fi

# 4. no cookies, no scripts, no third-party requests on any page
for p in "/" "/support.html" "/privacy.html"; do
  hdrs=$(curl -sI --max-time 20 "$BASE$p"); body=$(curl -s --max-time 20 "$BASE$p")
  echo "$hdrs" | grep -qi '^set-cookie' && fail "$p sets a cookie" || pass "no cookie on $p"
  echo "$body" | grep -qi '<script' && fail "$p contains <script>" || pass "no script on $p"
  ext=$(echo "$body" | grep -oE '(src|href)="https?://[^"]+"' | grep -vE 'teamdrybox\.com|knowwhatiown\.com' || true)
  [ -z "$ext" ] && pass "no third-party references on $p" || fail "$p references third parties: $ext"
done

# 5. content markers (what the App Store reviewer will actually look for)
curl -s "$BASE/" | grep -q 'Know What I Own' && pass "landing page names the app" || fail "landing page missing app name"
  curl -s "$BASE/" | grep -q 'href="support.html"' && pass "landing page links to support" || fail "landing page missing support link"
  curl -s "$BASE/" | grep -q 'href="privacy.html"' && pass "landing page links to privacy" || fail "landing page missing privacy link"
curl -s "$BASE/privacy.html" | grep -q 'Retention and Deletion' && pass "privacy policy complete" || fail "privacy policy missing sections"
curl -s "$BASE/support.html" | grep -q 'admin@teamdrybox.com' && pass "support page has contact" || fail "support page missing contact"

# 6. DNS and certificate (real domain only)
if [ "$HOST" = "knowwhatiown.com" ]; then
  ips=$(dig +short "$HOST" A | sort | tr '\n' ' ')
  for ip in 185.199.108.153 185.199.109.153 185.199.110.153 185.199.111.153; do
    echo "$ips" | grep -q "$ip" || fail "apex missing GitHub Pages IP $ip"
  done
  echo "$ips" | grep -q 185.199 && pass "apex points at GitHub Pages"
  end=$(echo | openssl s_client -servername "$HOST" -connect "$HOST:443" 2>/dev/null | openssl x509 -noout -enddate 2>/dev/null | cut -d= -f2)
  if [ -n "$end" ]; then
    days=$(( ( $(date -d "$end" +%s 2>/dev/null || date -j -f "%b %e %T %Y %Z" "$end" +%s) - $(date +%s) ) / 86400 ))
    [ "$days" -gt 14 ] && pass "certificate valid for $days more days" || fail "certificate expires in $days days"
  else fail "could not read certificate"; fi
fi

echo; [ "$fails" -eq 0 ] && echo "Smoke passed" || { echo "$fails failure(s)"; exit 1; }
