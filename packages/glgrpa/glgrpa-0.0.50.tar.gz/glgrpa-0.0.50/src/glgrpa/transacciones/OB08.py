import os
from ..SAP import SAP
from datetime import datetime, timedelta
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement


class OB08(SAP):
    titulo_pagina_inicio = 'Modificar vista "Tipos de cambio para la conversión": Resumen'
    
    def __init__(self, base_url: str, driver = None, dev: bool = False):
        super().__init__(base_url=base_url, driver=driver, dev=dev)
    
    def finalizar(self) -> None:
        """ Finaliza la transacción OB08. """
        self.mostrar("Finalizando transacción OB08")
        self.enviar_tecla_ventana('SHIFT', 'F3')
    
    def guardar(self) -> None:
        """ Guarda los cambios realizados en la transacción OB08. """
        self.mostrar("Guardando cambios en la transacción OB08")
        self.enviar_tecla_ventana('CTRL', 'S')
        
    def entradas_nuevas(self) -> bool:
        """ Accede a la página de entradas nuevas y espera a que se cargue correctamente durante 3 segundos."""
        reintentos = 0
        if self.driver.title == self.titulo_pagina_inicio:
            
            self.enviar_tecla_ventana('F5')
            
            nuevo_titulo_pagina = 'Entradas nuevas: Resumen de entradas añadidas'
            while self.driver.title != nuevo_titulo_pagina and reintentos < 3:
                self.demora(1)
                reintentos += 1
                
            if reintentos >= 3:
                self.mostrar("No se pudo acceder a la página de entradas nuevas después de 3 segundos", True)
                self.cerrar_navegador()
                return False
            
            self.mostrar("Accediendo a la página de entradas nuevas")
            
        elif self.driver.title == 'Actualizar vista de tabla: Acceso':
            self.mostrar("No se está en la página de entradas nuevas", True)
            raise ValueError("No se está en la página de entradas nuevas")
            
        return True
    
    def formato_fecha_cotizacion(self, formato: str = '%d/%m/%Y') -> str:
        """ Siempre es la fecha de ayer. Para el formato de entrada se debe usar '%d%m%Y' """
        fecha = datetime.now() - timedelta(days=1)
        return fecha.strftime(formato)
    
    def formato_divisa(self, valor_divisa: float) -> str:
        """ Formatea la divisa para que sea compatible con SAP. """
        return f"{valor_divisa:,.4f}".replace(",", "X").replace(".", ",").replace("X", ".")
    
    def formato_tipo_cotizacion(self, tipo: str) -> str:
        """ Formatea el tipo de cotización para que sea compatible con SAP """
        if tipo.lower() == 'compra':
            return 'B'
        elif tipo.lower() == 'venta':
            return 'G'
        else:
            raise ValueError("Tipo de cotización no válido. Debe ser 'compra' o 'venta'.")
    
    def formato_moneda(self, moneda: str) -> str:
        """ Formatea la moneda para que sea compatible con SAP """
        moneda = moneda.upper()
        if len(moneda) != 3 or not moneda.isalpha():
            raise ValueError("El código de moneda debe tener exactamente 3 letras (código ISO).")
        return moneda
    
    def armar_tabla(self, tipo: str, fecha: str, codigo_moneda: str, valor_divisa: str) -> str:
        """ Formatea la tabla para que sea compatible con SAP """
        self.mostrar(f"Armando tabla: {tipo}, {fecha}, {codigo_moneda}, {valor_divisa}")
        return f"{tipo}\t{fecha}\t\t\t\t{codigo_moneda}\t\t{valor_divisa}\t\t\tARS"
    
    def ingresar_tipo_de_cambio(self, tipo: str, codigo_moneda: str, valor_divisa: float) -> bool:
        """ Ingresa una nueva cotización en la tabla especificada. """
        if not self.entradas_nuevas():
            return False

        tipo = self.formato_tipo_cotizacion(tipo)
        fecha = self.formato_fecha_cotizacion('%d%m%Y')
        moneda = self.formato_moneda(codigo_moneda)
        valor_divisa_str = self.formato_divisa(valor_divisa)
        
        tabla = self.armar_tabla(tipo, fecha, moneda, valor_divisa_str)
        
        self.copiar_al_portapapeles(tabla)
        self.pegar_portapapeles_en_ventana_activa()
        self.guardar()
        
        alerta = self._alerta_transaccion()
        if alerta == "Los datos han sido grabados":
            self.mostrar("Tipo de cambio ingresado correctamente")
            self.finalizar()
            return True
        else:
            self.mostrar(f"Error al ingresar el tipo de cambio", True)
            self.mostrar(alerta, True)
            self.enviar_tecla_ventana('ESC')
            self.enviar_tecla_ventana('ENTER')
            self.cerrar_navegador()
        
        return False
    
    def _alerta_transaccion(self) -> str:
        """ Obtiene el texto de la alerta de transacción """
        self.mostrar("Obteniendo alerta de transacción")
        span_alerta, texto_alerta = self.buscar_elemento_en_iframes(By.CLASS_NAME, 'lsMessageBar')
        
        if span_alerta and texto_alerta:
            self.mostrar(f"Alerta encontrada")
            return texto_alerta.strip().split('\n')[0]
        
        self.mostrar("No se encontró alerta de transacción", True)
        return ""