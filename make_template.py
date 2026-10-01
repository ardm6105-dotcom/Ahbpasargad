"""Builds the PasarGuard subscription template from your own sub.html at docker build time."""
import os, sys
SRC, DST = sys.argv[1], sys.argv[2]
INJECT = r'''{% endraw %}
<script id="ahb-data" type="application/json">{{ {
  "username": user.username,
  "status": (user.status.value if user.status.value is defined else user.status|string),
  "used": (user.used_traffic or 0),
  "limit": (user.data_limit or 0),
  "expire": ((user.expire.timestamp()|int) if user.expire else 0),
  "links": links,
  "announce": announce or ""
} | tojson }}</script>
{% raw %}
<script>
(function(){
  var D={};try{D=JSON.parse(document.getElementById('ahb-data').textContent)}catch(e){}
  var fa=function(n,d){return Number(n).toLocaleString('fa-IR',{maximumFractionDigits:d==null?2:d})};
  var gb=function(b){return fa(b/1073741824,2)+' GB'};
  var set=function(id,v){var el=document.getElementById(id);if(el)el.textContent=v};
  var used=+D.used||0, limit=+D.limit||0, exp=+D.expire||0, now=Date.now()/1000;
  var unlimited=!limit;
  set('total-volume', unlimited?'نامحدود':gb(limit));
  set('used-volume', gb(used));
  set('remaining-volume', unlimited?'نامحدود':gb(Math.max(limit-used,0)));
  var pct=unlimited?0:Math.min(100,Math.round(used/limit*100));
  set('usage-percent', fa(pct,0)+'٪');
  var ring=document.querySelector('.overview-ring'); if(ring) ring.style.setProperty('--p',pct+'%');
  if(exp){
    var days=Math.max(0,Math.ceil((exp-now)/86400));
    set('remaining-days', fa(days,0)+' روز');
    try{set('expiry-date', new Date(exp*1000).toLocaleDateString('fa-IR',{year:'numeric',month:'long',day:'numeric'}))}catch(e){}
  } else { set('remaining-days','نامحدود'); set('expiry-date','بدون انقضا'); }
  var map={active:['فعال','green'],limited:['حجم تمام شده','orange'],expired:['منقضی شده','orange'],disabled:['غیرفعال','orange'],on_hold:['در انتظار اتصال','blue']};
  var st=map[D.status]||[D.status||'—','blue'];
  set('usage-status','وضعیت اشتراک: '+st[0]);
  var sEl=document.getElementById('subscription-status'); if(sEl){sEl.textContent=st[0];sEl.className=st[1];}
  if(D.announce){var a=document.getElementById('announce');if(a){a.textContent=D.announce;a.classList.remove('hidden')}}
  var subUrl=location.origin+location.pathname.replace(/\/(info|usage|links|v2ray|clash|sing-box).*$/,'');
  var subRow=document.querySelector('#connections-list .conn-row[data-copy="sub"] .sub'); if(subRow) subRow.textContent=subUrl;
  var links=(D.links||[]).filter(Boolean);
  var allRow=document.querySelector('#connections-list .conn-row[data-copy="all"] .sub'); if(allRow) allRow.textContent=fa(links.length,0)+' مورد';
  document.querySelectorAll('#connections-list .conn-row[data-copy="link"]').forEach(function(row,i){
    var el=row.querySelector('.sub');
    if(links[i]){ if(el) el.textContent=links[i]; } else { row.style.display='none'; }
  });
  var lc=document.getElementById('login-card'); if(lc) lc.classList.add('hidden');
})();
</script>'''
html = open(SRC, encoding="utf-8").read()
i = html.find("<script")
if i < 0: i = html.rfind("</body>")
out = "{% raw %}" + html[:i] + "\n" + INJECT + "\n" + html[i:] + "{% endraw %}"
os.makedirs(os.path.dirname(DST), exist_ok=True)
open(DST, "w", encoding="utf-8").write(out)
print("template ok", len(out))
