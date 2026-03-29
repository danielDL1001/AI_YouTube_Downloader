def create_progress_hook(progress, total_ref):
    def progresso_hook(d):
        if d["status"] == "finished":
            info = d.get("info_dict", {})
            if info.get("_type") != "playlist":
                total_ref["current"] += 1
                now = total_ref["current"]
                all_items = total_ref["total"]
                pct = int((now / all_items) * 100)
                progress(pct, now, all_items, None, None)

        if d["status"] == "downloading":
            speed = d.get("speed", 0)
            eta = d.get("eta", 0)

            if speed:
                speed_mb = speed / 1024 / 1024
                speed_text = f"{speed_mb:.2f} MB/s"
            else:
                speed_text = "Calculando..."

            if eta:
                mins = eta // 60
                secs = eta % 60
                eta_text = f"{mins:02d}:{secs:02d}"
            else:
                eta_text = "--:--"

            progress(None, None, None, speed_text, eta_text)

    return progresso_hook