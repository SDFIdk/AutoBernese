import datetime as dt

import pytest

from ab.bsw.bpe import (
    as_environment_variables,
    parse_bpe_terminal_output,
    BPETerminalOutput,
)


def test_as_environment_variables():
    whatever = ""
    _input = {
        "foo": whatever,
        "bar": whatever,
    }
    expected = {
        "AB_BPE_FOO": whatever,
        "AB_BPE_BAR": whatever,
    }
    result = as_environment_variables(_input)
    assert result == expected, f"Expected {result!r} to be {expected!r} ..."

    _input = {
        0: whatever,
    }
    with pytest.raises(TypeError):
        as_environment_variables(_input)

    _input = {
        "foo bar": whatever,
    }
    with pytest.raises(ValueError):
        as_environment_variables(_input)


def test_parse_bpe_terminal_output():
    output_success = """\
CPU File ${U}/PAN/USER.CPU has been reset

Starting BPE on 10-Jan-2024 15:03:50
------------------------------------
<USERNAME>@

PCFile:         ${U}/PCF/ITRF.PCF
CPU file:       ${U}/PAN/USER.CPU
Campaign:       ${P}/EXAMPLE
Year/session:   2021/0960
BPE output:     ${P}/EXAMPLE/BPE/ITRF_0960.OUT
BPE status:     ${P}/EXAMPLE/BPE/ITRF_0960.RUN

BPE server runs PID = 24792

BPE finished at 10-Jan-2024 15:04:14
------------------------------------

"""
    result = parse_bpe_terminal_output(output_success)
    expected = BPETerminalOutput(
        beg=dt.datetime(2024, 1, 10, 15, 3, 50),
        username="<USERNAME>",
        pcf_file="${U}/PCF/ITRF.PCF",
        cpu_file="${U}/PAN/USER.CPU",
        campaign="${P}/EXAMPLE",
        year_session="2021/0960",
        output_file="${P}/EXAMPLE/BPE/ITRF_0960.OUT",
        status_file="${P}/EXAMPLE/BPE/ITRF_0960.RUN",
        server_pid="24792",
        end=dt.datetime(2024, 1, 10, 15, 4, 14),
        ok=True,
    )
    assert result == expected, f"Expected {result!r} to be {expected!r} ..."

    substitutes = dict(
        P='/home/bsw/dev/data/CAMPAIGN54',
        U='/home/user/bsw/dev/user',
    )
    result_substituted = parse_bpe_terminal_output(output_success, substitutes)
    expected_substituted = BPETerminalOutput(
        beg=dt.datetime(2024, 1, 10, 15, 3, 50),
        username="<USERNAME>",
        pcf_file="/home/user/bsw/dev/user/PCF/ITRF.PCF",
        cpu_file="/home/user/bsw/dev/user/PAN/USER.CPU",
        campaign="/home/bsw/dev/data/CAMPAIGN54/EXAMPLE",
        year_session="2021/0960",
        output_file="/home/bsw/dev/data/CAMPAIGN54/EXAMPLE/BPE/ITRF_0960.OUT",
        status_file="/home/bsw/dev/data/CAMPAIGN54/EXAMPLE/BPE/ITRF_0960.RUN",
        server_pid="24792",
        end=dt.datetime(2024, 1, 10, 15, 4, 14),
        ok=True,
    )
    assert result_substituted == expected_substituted, f"Expected {result!r} to be {expected!r} ..."

    output_failed = """\
CPU File ${U}/PAN/USER.CPU has been reset

Starting BPE on 10-Jan-2024 15:03:50
------------------------------------
<USERNAME>@

PCFile:         ${U}/PCF/ITRF.PCF
CPU file:       ${U}/PAN/USER.CPU
Campaign:       ${P}/EXAMPLE
Year/session:   2021/0960
BPE output:     ${P}/EXAMPLE/BPE/ITRF_0960.OUT
BPE status:     ${P}/EXAMPLE/BPE/ITRF_0960.RUN

BPE server runs PID = 24792

User script error in: ${P}/EXAMPLE/BPE/ITRF_0950.OUT

BPE finished at 10-Jan-2024 15:04:14
------------------------------------

"""
    result = parse_bpe_terminal_output(output_failed)
    expected = BPETerminalOutput(
        beg=dt.datetime(2024, 1, 10, 15, 3, 50),
        username="<USERNAME>",
        pcf_file="${U}/PCF/ITRF.PCF",
        cpu_file="${U}/PAN/USER.CPU",
        campaign="${P}/EXAMPLE",
        year_session="2021/0960",
        output_file="${P}/EXAMPLE/BPE/ITRF_0960.OUT",
        status_file="${P}/EXAMPLE/BPE/ITRF_0960.RUN",
        server_pid="24792",
        end=dt.datetime(2024, 1, 10, 15, 4, 14),
        ok=False,
    )
    assert result == expected, f"Expected {result!r} to be {expected!r} ..."
