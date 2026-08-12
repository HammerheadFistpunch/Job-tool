from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from backend.review import ReviewQueueService
from backend.storage.database import connect_database, initialize_database


app = FastAPI(title="JobIntel")


class ReviewUpdate(BaseModel):
    review_state: str = "new"
    match_label: str | None = None
    reason_codes: list[str] = Field(default_factory=list)
    notes: str = ""


@app.on_event("startup")
def startup():
    connection = connect_database()
    try:
        initialize_database(connection)
    finally:
        connection.close()


@app.get("/api/status")
def status():
    service = ReviewQueueService()
    return {"status": "JobIntel online", "profile_version": service.profile.profile_version}


@app.get("/api/jobs")
def jobs():
    service = ReviewQueueService()
    return {"profile_version": service.profile.profile_version, "jobs": service.list_jobs()}


@app.patch("/api/jobs/{job_id}/review")
def update_review(job_id: int, update: ReviewUpdate):
    try:
        return ReviewQueueService().save_review(
            job_id, update.review_state, update.match_label, update.reason_codes, update.notes
        )
    except KeyError as error:
        raise HTTPException(status_code=404, detail=str(error)) from error
    except ValueError as error:
        raise HTTPException(status_code=422, detail=str(error)) from error


@app.get("/", response_class=HTMLResponse)
def review_queue():
    return HTMLResponse(REVIEW_QUEUE_HTML)


REVIEW_QUEUE_HTML = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>JobIntel Review Queue</title><style>
:root{color-scheme:dark;--bg:#101418;--panel:#192027;--line:#34404a;--text:#edf3f7;--muted:#a9b6bf;--accent:#78d6c6;--danger:#ff9a9a}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--text);font:15px/1.5 system-ui,sans-serif}header{position:sticky;top:0;z-index:2;padding:18px max(18px,calc((100vw - 1200px)/2));background:#101418ee;border-bottom:1px solid var(--line);backdrop-filter:blur(12px)}h1{margin:0 0 12px;font-size:24px}.controls{display:flex;gap:10px;flex-wrap:wrap}select,input,textarea,button{color:var(--text);background:#11171c;border:1px solid var(--line);border-radius:7px;padding:9px;font:inherit}button{cursor:pointer;background:#254c47;border-color:#3d766d}button:hover{background:#30615a}main{max-width:1200px;margin:auto;padding:20px}#summary{color:var(--muted);margin-bottom:14px}.job{background:var(--panel);border:1px solid var(--line);border-radius:12px;padding:18px;margin-bottom:14px}.job h2{margin:0;font-size:20px}.job h2 a{color:var(--text)}.meta,.reason{color:var(--muted)}.badges{display:flex;flex-wrap:wrap;gap:7px;margin:10px 0}.badge{padding:3px 8px;border-radius:999px;background:#28343c;font-size:13px}.eligible{color:var(--accent)}.ineligible{color:var(--danger)}.needs_review{color:#ffd28a}details{border-top:1px solid var(--line);padding-top:10px;margin-top:10px}summary{cursor:pointer}.review{display:grid;grid-template-columns:145px 165px 210px 1fr auto;gap:9px;margin-top:14px;align-items:start}.review-reasons{min-height:74px}textarea{min-height:74px;resize:vertical}.empty{padding:40px;text-align:center;color:var(--muted)}@media(max-width:900px){.review{grid-template-columns:1fr}header{position:static}}
</style></head><body><header><h1>JobIntel Review Queue</h1><div class="controls">
<select id="eligibility"><option value="">All eligibility</option><option>eligible</option><option>needs_review</option><option>ineligible</option></select>
<select id="state"><option value="">All review states</option><option>new</option><option>saved</option><option>dismissed</option><option>applied</option><option>interviewed</option><option>rejected</option></select>
<input id="search" type="search" placeholder="Search title or company"><button id="reload">Refresh</button></div></header>
<main><div id="summary">Loading…</div><div id="jobs"></div></main><script>
const states=['new','saved','dismissed','applied','interviewed','rejected'],labels=['','strong_match','consider','weak_match','reject','hard_reject'],reasons=['responsibilities_fit','strong_evidence_match','career_progression','preferred_industry','compensation','location_or_remote_fit','organization_or_mission','learning_opportunity','seniority_mismatch','sales_or_quota_emphasis','missing_required_qualification','schedule_travel_or_workload','poor_organization_signals'];let allJobs=[],profileVersion='';
const esc=value=>String(value??'').replace(/[&<>"']/g,c=>({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
const options=(items,current)=>items.map(v=>`<option ${v===current?'selected':''}>${esc(v)}</option>`).join('');
const reasonOptions=current=>reasons.map(v=>`<option value="${v}" ${current.includes(v)?'selected':''}>${esc(v.replaceAll('_',' '))}</option>`).join('');
async function load(){const response=await fetch('/api/jobs');if(!response.ok)throw new Error(await response.text());const data=await response.json();allJobs=data.jobs;profileVersion=data.profile_version;render()}
function render(){const e=document.querySelector('#eligibility').value,s=document.querySelector('#state').value,q=document.querySelector('#search').value.toLowerCase();const jobs=allJobs.filter(j=>(!e||j.eligibility_status===e)&&(!s||j.review_state===s)&&(!q||`${j.title} ${j.company}`.toLowerCase().includes(q)));document.querySelector('#summary').textContent=`${jobs.length} of ${allJobs.length} jobs · profile ${profileVersion}`;document.querySelector('#jobs').innerHTML=jobs.length?jobs.map(card).join(''):'<div class="empty">No jobs match these filters.</div>'}
function card(j){const eligibilityReasons=j.eligibility_reasons.map(r=>`<li><strong>${esc(r.explanation)}</strong>${r.evidence?`<div class="reason">Evidence: ${esc(r.evidence)}</div>`:''}</li>`).join('');return `<article class="job" data-id="${j.database_id}"><h2>${j.canonical_url?`<a href="${esc(j.canonical_url)}" target="_blank" rel="noopener">${esc(j.title)}</a>`:esc(j.title)}</h2><div class="meta">${esc(j.company)} · ${esc(j.location||'Location not stated')} · ${esc(j.source)}</div><div class="badges"><span class="badge ${j.eligibility_status}">${esc(j.eligibility_status)}</span><span class="badge">${esc(j.review_state)}</span>${j.match_label?`<span class="badge">${esc(j.match_label)}</span>`:''}</div><details><summary>Eligibility explanation</summary><ul>${eligibilityReasons}</ul></details><details><summary>Posting text</summary><p>${esc(j.description).replace(/\n/g,'<br>')}</p></details><div class="review"><select class="review-state" aria-label="Review state">${options(states,j.review_state)}</select><select class="match-label" aria-label="Match label">${options(labels,j.match_label||'')}</select><select class="review-reasons" multiple aria-label="Interest or rejection reasons">${reasonOptions(j.reason_codes)}</select><textarea class="notes" placeholder="Notes">${esc(j.notes)}</textarea><button onclick="save(${j.database_id})">Save review</button></div></article>`}
async function save(id){const card=document.querySelector(`[data-id="${id}"]`),button=card.querySelector('button');button.disabled=true;button.textContent='Saving…';const reasonCodes=Array.from(card.querySelector('.review-reasons').selectedOptions).map(option=>option.value);const response=await fetch(`/api/jobs/${id}/review`,{method:'PATCH',headers:{'Content-Type':'application/json'},body:JSON.stringify({review_state:card.querySelector('.review-state').value,match_label:card.querySelector('.match-label').value||null,reason_codes:reasonCodes,notes:card.querySelector('.notes').value})});if(!response.ok){button.textContent='Save failed';button.disabled=false;return}const review=await response.json(),job=allJobs.find(j=>j.database_id===id);Object.assign(job,review);button.textContent='Saved';setTimeout(()=>{button.textContent='Save review';button.disabled=false;render()},600)}
['eligibility','state','search'].forEach(id=>document.querySelector('#'+id).addEventListener('input',render));document.querySelector('#reload').addEventListener('click',load);load().catch(error=>document.querySelector('#summary').textContent=`Unable to load: ${error.message}`);
</script></body></html>'''
