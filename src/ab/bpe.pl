# use lib $ENV{BPE};
use startBPE;
# use bpe_util;

my $bpe = new startBPE();

$$bpe{PCF_FILE}     = "NKG_ATX";
$$bpe{CPU_FILE}     = "USER";
$$bpe{BPE_CAMPAIGN} = "NKG$gpsweek";
$$bpe{YEAR}         = $yyyy;
$$bpe{SESSION}      = "${doystr}0";
$$bpe{SYSOUT}       = "ATX2PCV";
$$bpe{STATUS}       = "ATX2PCV.RUN";
$$bpe{TASKID}       = "A2P";

$bpe->resetCPU();
$bpe->run();

# ---
