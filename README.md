### NFI

Case management for neonatal sponsorship programs, built on Frappe. Hospitals submit cases for newborns who need NICU support; NFI coordinators verify them, run medical / social / financial reviews, a director approves the amount, and the accountant records payment after discharge.

Includes the case workflow (BRP, BCRP, BARP, TBC, SRT programs), role workspaces, a coordinator Case Desk, a Payments page, print formats, approval / rejection emails and register reports. See `docs/phases.md` for scope and `docs/backend.md` for the data model.

### Demo data

```bash
bench --site $SITE execute nfi.demo.make   # demo hospitals, cases and one user per role (password: admin)
bench --site $SITE execute nfi.demo.clear
```

### Installation

You can install this app using the [bench](https://github.com/frappe/bench) CLI:

```bash
cd $PATH_TO_YOUR_BENCH
bench get-app $URL_OF_THIS_REPO --branch develop
bench install-app nfi
```

### Contributing

This app uses `pre-commit` for code formatting and linting. Please [install pre-commit](https://pre-commit.com/#installation) and enable it for this repository:

```bash
cd apps/nfi
pre-commit install
```

Pre-commit is configured to use the following tools for checking and formatting your code:

- ruff
- eslint
- prettier
- pyupgrade

### License

MIT
