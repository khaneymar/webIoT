var enblPort;   // ドライバのENBLポート(PWM) : 16
var phasePort;  // ドライバのPHASEポート     : 20
var openswitchPort;     // 窓が開いた時のスイッチのポート : 23
var closeswitchPort;    // 窓が閉じた時のスイッチのポート : 24

var openswval;     // 窓が開いたときに押されるスイッチ
var closeswval;    // 窓が閉じたときに押されるスイッチ

async function open(){
    phasePort.write(1);
    
    while (openswval === 0){
        enblPort.write(1);
	await sleep(50);
    }
    enblPort.write(0);
}

window.onload = async function main(){
    var order = "";
    var gpioAccess = await navigator.requestGPIOAccess();

    openswitchPort = gpioAccess.ports.get(5);
    await openswitchPort.export("in");

    closeswitchPort = gpioAccess.ports.get(6);
    await closeswitchPort.export("in");

    enblPort = gpioAccess.ports.get(16);
    await enblPort.export("out");

    phasePort = gpioAccess.ports.get(20);
    await phasePort.export("out");

    order = "open";

    for(;;){
        openswval = await openswitchPort.read();
        if (openswval === 255) openswval = 1;
        openswval = openswval === 0 ? 1 : 0;
        if (order == "open"){
            open();
            order = "";
        }
        await sleep(100);

    }
    

}
