#!/usr/bin/perl -w
use lib $ENV{BPE};
use startBPE;

my $bpe = new startBPE();

$$bpe{PCF_FILE}     = "$ENV{ab_bpe_pcf_file}";
$$bpe{CPU_FILE}     = "$ENV{ab_bpe_cpu_file}";
$$bpe{BPE_CAMPAIGN} = "$ENV{ab_bpe_bpe_campaign}";
$$bpe{YEAR}         = "$ENV{ab_bpe_year}";
$$bpe{SESSION}      = "$ENV{ab_bpe_session}";
$$bpe{SYSOUT}       = "$ENV{ab_bpe_sysout}";
$$bpe{STATUS}       = "$ENV{ab_bpe_status}";
$$bpe{TASKID}       = "$ENV{ab_bpe_taskid}";

$bpe->resetCPU();
$bpe->run();
