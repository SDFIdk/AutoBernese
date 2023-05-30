#!/usr/bin/perl
use lib $ENV{BPE};
use startBPE;

my $bpe = new startBPE();

$$bpe{PCF_FILE}     = "$ENV{AB_BPE_PCF_FILE}";
$$bpe{CPU_FILE}     = "$ENV{AB_BPE_CPU_FILE}";
$$bpe{BPE_CAMPAIGN} = "$ENV{AB_BPE_CAMPAIGN}";
$$bpe{YEAR}         = "$ENV{AB_BPE_YEAR}";
$$bpe{SESSION}      = "$ENV{AB_BPE_SESSION}";
$$bpe{SYSOUT}       = "$ENV{AB_BPE_SYSOUT}";
$$bpe{STATUS}       = "$ENV{AB_BPE_STATUS}";
$$bpe{TASKID}       = "$ENV{AB_BPE_TASKID}";

$bpe->resetCPU();
$bpe->run();
