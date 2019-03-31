start labrad

TIMEOUT /T 7

start python "%CD%\DEMONS Servers\serial_server.py"

TIMEOUT /T 1

start python "%CD%\DEMONS Servers\gpib_server.py"
TIMEOUT /T 1

start python "%CD%\DEMONS Servers\gpib_device_manager.py"
TIMEOUT /T 1

start python "%CD%\DEMONS Servers\data_vault.py"
TIMEOUT /T 1

start python "%CD%\DEMONS Servers\dac_adc.py"
TIMEOUT /T 1

start python "%CD%\DEMONS Servers\SR830.py"

python "%CD%\DEMONS GUI\DEMONS.py"

pause