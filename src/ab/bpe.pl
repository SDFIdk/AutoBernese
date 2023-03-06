use lib $ENV{BPE};
use startBPE;

my $bpe = new startBPE();

$$bpe{PCF_FILE}     = "PPP";
$$bpe{CPU_FILE}     = "USER";
$$bpe{BPE_CAMPAIGN} = "EXAMPLE";
$$bpe{YEAR}         = "2019";
$$bpe{SESSION}      = "0440";
$$bpe{SYSOUT}       = "PPP";
$$bpe{STATUS}       = "PPP.RUN";
$$bpe{TASKID}       = "PP";

$bpe->resetCPU();
$bpe->run();
