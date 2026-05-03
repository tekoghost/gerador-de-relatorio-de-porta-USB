import platform
import subprocess
import json
from datetime import datetime

def get_usb_devices():
    os_name = platform.system()
    devices = []

    try:
        if os_name == "Windows":
            # Usa o PowerShell para listar dispositivos Plug and Play filtrando por USB
            cmd = [
                'powershell', 
                '-Command', 
                "Get-PnpDevice -PresentOnly | Where-Object { $_.InstanceId -match '^USB' } | Select-Object Status, Class, FriendlyName, InstanceId | ConvertTo-Json"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            if result.stdout:
                devices = json.loads(result.stdout)

        elif os_name == "Linux":
            # Usa o comando nativo lsusb no Linux
            cmd = ['lsusb']
            result = subprocess.run(cmd, capture_output=True, text=True)
            for line in result.stdout.split('\n'):
                if line.strip():
                    devices.append({"Descrição": line.strip()})
        
        elif os_name == "Darwin":
            # Usa o system_profiler no macOS
            cmd = ['system_profiler', 'SPUSBDataType', '-json']
            result = subprocess.run(cmd, capture_output=True, text=True)
            if result.stdout:
                data = json.loads(result.stdout)
                devices = data.get('SPUSBDataType', [])
        else:
            print(f"Sistema operacional {os_name} não suportado nativamente.")

    except Exception as e:
        print(f"Erro ao buscar dispositivos: {e}")

    # Garante que o retorno seja sempre uma lista
    if isinstance(devices, dict):
        devices = [devices]
        
    return devices

def generate_report(devices):
    # Cria um nome de arquivo único baseado na data e hora
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"relatorio_usb_{timestamp}.txt"
    
    with open(filename, 'w', encoding='utf-8') as f:
        f.write("=== Relatório de Dispositivos USB ===\n")
        f.write(f"Gerado em: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
        f.write(f"Sistema Operacional: {platform.system()}\n")
        f.write("-" * 45 + "\n")
        
        if not devices:
            f.write("\nNenhum dispositivo USB encontrado ou ocorreu um erro na leitura.\n")
        else:
            for idx, dev in enumerate(devices, 1):
                f.write(f"\n[Dispositivo {idx}]\n")
                if isinstance(dev, dict):
                    # Formata as chaves e valores do dicionário
                    for key, value in dev.items():
                        # Evita imprimir estruturas aninhadas complexas de forma feia (comum no macOS)
                        if isinstance(value, (list, dict)):
                            f.write(f"  {key}: [Dados Complexos Omitidos]\n")
                        else:
                            f.write(f"  {key}: {value}\n")
                else:
                    f.write(f"  Info: {dev}\n")
                    
    print(f"\n[+] Relatório gerado com sucesso: {filename}")

if __name__ == "__main__":
    print("Iniciando varredura de portas USB...")
    usb_list = get_usb_devices()
    generate_report(usb_list)