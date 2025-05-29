from datetime import datetime, time
import requests
from flask import Flask, render_template, request


app = Flask(
    __name__,
    template_folder="templates",
    static_folder="static"
)


machines = ["sftp1", "sftp2", "sftp3"]
API_URL = __import__("os").environ.get("API_URL", "http://api:8000")


date_format = "%Y-%m-%d"
time_format = "%H:%M:%S"


def load_logs(date: datetime, machine: str) -> dict[str, list[datetime]]:
    params = {
        "machine_name": machine,
        "date": date.strftime(date_format),
    }
    resp = requests.get(f"{API_URL}/query", params=params, timeout=5)
    resp.raise_for_status()
    raw = resp.json()

    result: dict[str, list[datetime]] = {}
    for row in raw:
        tbl = row["table_name"]
        t_str = row["time"]
        try:
            t = time.fromisoformat(t_str)
            result.setdefault(tbl, []).append(t)
        except ValueError:
            continue
    return result


def aggregate_half_hour(entries: list[datetime]) -> list[int]:
    bins = [0] * 48
    for dt in entries:
        idx = dt.hour * 2 + (dt.minute // 30)
        bins[idx] += 1
    return bins

@app.route('/', methods=['GET', 'POST'])
def index():
    selected = None
    selected_machine = None
    slots = [f"{i//2:02d}:{'00' if i%2==0 else '30'}" for i in range(48)]
    data = {}
    has_logs = False

    if request.method == 'POST':
        date_str = request.form.get('date')
        selected_machine = request.form.get('machine')

        if date_str:
            try:
                selected = datetime.fromisoformat(date_str)
            except ValueError:
                selected = None

        if selected and selected_machine in machines:
            raw = load_logs(selected, selected_machine)
            for fname, entries in raw.items():
                counts = aggregate_half_hour(entries)
                mmax = max(counts) if any(counts) else 0
                data[fname] = {'counts': counts, 'max': mmax}
                if mmax > 0:
                    has_logs = True

    return render_template(
        'index.html',
        machines=machines,
        selected=selected,
        selected_machine=selected_machine,
        slots=slots,
        data=data,
        has_logs=has_logs
    )

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4000)
