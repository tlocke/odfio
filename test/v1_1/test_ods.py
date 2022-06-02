import os
import zipfile

from datetime import datetime as Datetime

import odio


def normalize_walk(path):
    return list(
        [os.path.relpath(pth, path), sorted(dirs), sorted(fls)]
        for pth, dirs, fls in sorted(os.walk(path))
    )


def test_writerow(tmpdir):
    TABLE_NAME = "Plan"
    ROW = ["veni, vidi, vici", 0.3, 5, Datetime(2015, 6, 30, 16, 38), None]
    fname = tmpdir.join("actual.ods")
    with open(str(fname), "wb") as f:
        with odio.create_spreadsheet(f, "1.1") as sheet:
            table = sheet.append_table(TABLE_NAME)
            table.append_row(ROW)
    actual_dir = str(tmpdir.mkdir("actual"))
    with zipfile.ZipFile(str(fname)) as z:
        z.extractall(str(actual_dir))

    desired_dir = str(os.path.join(os.path.dirname(__file__), "unpacked"))

    actual_walk = normalize_walk(actual_dir)
    desired_walk = normalize_walk(desired_dir)
    assert actual_walk == desired_walk

    for i, (actual_pth, actual_dirs, actual_fls) in enumerate(actual_walk):
        desired_pth, desired_dirs, desired_fls = desired_walk[i]
        for j, actual_fl in enumerate(actual_fls):
            desired_fl = desired_fls[j]
            with open(
                os.path.join(actual_dir, actual_pth, actual_fl)
            ) as actual_f, open(
                os.path.join(desired_dir, desired_pth, desired_fl)
            ) as desired_f:
                assert "".join(actual_f) == "".join(desired_f)

    with open(str(fname), "rb") as f:
        sheet = odio.parse_spreadsheet(f)
        table = sheet.tables[0]
        assert table.name == TABLE_NAME
        assert table.rows[0] == ROW


def test_file_not_closed(tmpdir):
    fname = tmpdir.join("test.ods")
    f = open(str(fname), "wb")
    with odio.create_spreadsheet(f, "1.1") as sheet:
        table = sheet.append_table("Keats")
        table.append_row(("Season", "of", "mists"))
    f.seek(0)
    f.close()
