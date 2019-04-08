start /min labrad

TIMEOUT 7 /NOBREAK

start /min python "%CD%\DEMONS Servers\serial_server.py"

TIMEOUT 1 /NOBREAK

start /min python "%CD%\DEMONS Servers\gpib_server.py"

TIMEOUT 1 /NOBREAK

start /min python "%CD%\DEMONS Servers\gpib_device_manager.py"

TIMEOUT 1 /NOBREAK

start /min python "%CD%\DEMONS Servers\data_vault.py"

TIMEOUT 1 /NOBREAK

start /min python "%CD%\DEMONS Servers\dac_adc.py"

TIMEOUT 1 /NOBREAK

start /min python "%CD%\DEMONS Servers\SR830.py"

TIMEOUT 1 /NOBREAK

start /min python "%CD%\DEMONS Servers\SR860.py"

TIMEOUT 1 /NOBREAK

start /min python "%CD%\DEMONS Servers\SIM_900.py"

TIMEOUT 1 /NOBREAK

start /min python "%CD%\DEMONS Servers\ips_120_10.py"

TIMEOUT 1 /NOBREAK

start /min python "%CD%\DEMONS Servers\ami_430.py"

TIMEOUT 1 /NOBREAK

python "%CD%\DEMONS GUI\DEMONS.py"

pause