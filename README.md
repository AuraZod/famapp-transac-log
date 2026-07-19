<div align="center">
  <img src="https://capsule-render.vercel.app/api?type=waving&color=4361ee&height=200&section=header&text=famapp-transac-log&fontSize=40&fontColor=fff&animation=twinkling&fontAlignY=35"/>
  
  <br/>
  
  <img src="https://readme-typing-svg.herokuapp.com?font=Fira+Code&size=18&duration=3000&pause=1000&color=4361EE&center=true&vCenter=true&width=500&lines=Pluggable+Ledger+Logging;Local+SQLite+%26+Cloud+Supabase;Double-Claim+Replay+Protection" alt="Typing SVG" />
  
  <br/>

[![PyPI Version](https://img.shields.io/badge/pypi-v0.1.0-blueviolet?style=for-the-badge&logo=pypi)](https://pypi.org/)
[![Database](https://img.shields.io/badge/db-sqlite%20%7C%20supabase%20%7C%20memory-blue?style=for-the-badge)](https://www.sqlite.org/)
[![License](https://img.shields.io/badge/license-MIT-green?style=for-the-badge)](https://opensource.org/licenses/MIT)

<br/>
<img src="assets/transac_log_banner.png" width="100%" alt="famapp-transac-log Illustration" />

</div>

---

### `>_ root@famapp:~/ledger# ./verify_loop.sh`

```text
Incoming Verification Request
              │
              ▼
   [ Check Replay Database ] ──► is_verified() ?
              │
      ┌───────┴───────┐
      ▼ (Yes)         ▼ (No)
[Reject Replay]   [Log & Commit to Ledger]
```

---

### `>_ root@famapp:~/ledger# cat storage_adapters.cfg`

*   **`SQLiteLedger` (DEFAULT):** Writes logs to a local file (`payments.db`). Perfect for standard standalone servers. Requires zero hosting or setup.
*   **`MemoryLedger`:** An in-memory ledger with automated Time-To-Live (TTL) record pruning. Best for tests or single-session checkouts.
*   **`SupabaseLedger`:** Synchronizes your transaction data to a hosted Supabase PostgreSQL table. Recommended for scalable multi-server production systems.

---

### `>_ root@famapp:~/ledger# python example.py`

```python
from famapp_transac_log import SQLiteLedger

ledger = SQLiteLedger(db_path="my_payments.db")

is_claimed = ledger.is_verified(utr="123456789012")
if not is_claimed:
    ledger.save_verification(
        status=200,
        endpoint="verify_payment",
        amount=150.00,
        utr="123456789012",
        sender_name="Mr Ramesh Kumar"
    )
```

---

### Open Source Contribution

This project is fully open source. We encourage and welcome contributions from the community to help improve, optimize, and extend the ecosystem. Feel free to open issues or submit pull requests!

## 🪪 License
This project is licensed under the [MIT License](https://opensource.org/licenses/MIT). See the [LICENSE](LICENSE) file for details.

---

### Contributors 👥
<a href="https://github.com/AuraZod/famapp-transac-log/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=AuraZod/famapp-transac-log" />
</a>
