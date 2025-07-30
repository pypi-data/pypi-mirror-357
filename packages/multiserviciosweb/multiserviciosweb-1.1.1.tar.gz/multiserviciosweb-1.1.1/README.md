# **ValidaCurp Python Client**

[![PyPI version](https://badge.fury.io/py/multiserviciosweb.svg)](https://badge.fury.io/py/multiserviciosweb)
[![Python versions](https://img.shields.io/pypi/pyversions/multiserviciosweb.svg)](https://pypi.org/project/multiserviciosweb/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

* This library can validate, calculate and obtain CURP information in México.

* Copyright (c) Multiservicios Web JCA S.A. de C.V., https://multiservicios-web.com.mx
* More information: https://valida-curp.com.mx
* License: MIT (https://opensource.org/license/MIT)

## 1. Requirements

- Python 3.7 or later
- Instalación automática de dependencias (`requests` y `python-dotenv`)

## 2. Installation

You can install this package via pip:

```bash
pip install multiserviciosweb
```

## 3. Account

### 3.1. Create an account

Create an account following this link: https://valida-curp.com.mx/registro

### 3.2. Create a project

Create a project following this link: https://valida-curp.com.mx/proyectos/crear

### 3.3. Get token

Get your token from project dashboard: https://valida-curp.com.mx/proyectos

## **4. Usage**

### 4.1. Import library

```python
from MultiServiciosWeb import ValidaCurp, ValidaCurpException
```

### 4.2. Create instance

You can provide token in 3 ways:

```python
# Option 1: Directly in constructor
valida_curp = ValidaCurp('YOUR-TOKEN')
```

```python
# Option 2: Environment variable (.env file)
# .env content:
# TOKEN_VALIDA_API_CURP = 'YOUR-TOKEN'

valida_curp = ValidaCurp()
```

```python
# Option 3: System environment variable
# export TOKEN_VALIDA_API_CURP='YOUR-TOKEN'

valida_curp = ValidaCurp()
```

### 4.3. (Optional) Set API Version

You can set the API version (1 or 2). Default is 2:

```python
valida_curp.set_version(2)  # 1 for legacy, 2 for current
```

### 4.4. (Optional) Custom Endpoint

```python
valida_curp = ValidaCurp(
    token='YOUR-TOKEN',
    custom_endpoint='https://custom.valida-curp.com.mx/'
)
```

## 5. Methods

### 5.1. Validate CURP

```python
validation_result = valida_curp.is_valid('BUME980528HDFRCD02')
print(validation_result)
# Output: {'valido': True} or {'valido': False}
```

### 5.2. Get CURP data

```python
curp_data = valida_curp.get_data('BUME980528HDFRCD02')
print(curp_data)
# Output: Dictionary with CURP information
```

### 5.3. Calculate CURP

```python
person_data = {
    'names': 'Juan Carlos',
    'lastName': 'García',
    'secondLastName': 'López',
    'birthDay': '15',
    'birthMonth': '08',
    'birthYear': '1990',
    'gender': 'H',  # H: Hombre, M: Mujer
    'entity': '09'  # CDMX
}

result = valida_curp.calculate(person_data)
print(result)
# Output: {'curp': 'GALJ900815HDFRPN01'}
```

### 5.4. Get entities

```python
entities = valida_curp.get_entities()
print(entities)
# Output: Dictionary with all Mexican states and codes
```

## 6. Full Example

```python
from MultiServiciosWeb import ValidaCurp, ValidaCurpException

try:
    # Initialize client
    valida_curp = ValidaCurp('YOUR-TOKEN')
    
    # 1. Validate CURP
    print("Validating CURP:", valida_curp.is_valid('BUME980528HDFRCD02'))
    
    # 2. Get CURP data
    print("CURP data:", valida_curp.get_data('BUME980528HDFRCD02'))
    
    # 3. Calculate CURP
    person_data = {
        'names': 'María Fernanda',
        'lastName': 'Hernández',
        'secondLastName': 'Jiménez',
        'birthDay': '22',
        'birthMonth': '11',
        'birthYear': '1985',
        'gender': 'M',
        'entity': '14'  # Jalisco
    }
    print("Calculated CURP:", valida_curp.calculate(person_data))
    
    # 4. Get entities
    print("Entities:", valida_curp.get_entities())
    
    # 5. Switch to API v1
    valida_curp.set_version(1)
    print("Entities (v1):", valida_curp.get_entities())

except ValidaCurpException as e:
    print(f"API Error: {e}")
except Exception as e:
    print(f"General Error: {e}")
```

## 7. Error Handling

Handle specific errors:

```python
try:
    valida_curp.get_data('INVALID-CURP')
except ValidaCurpException as e:
    if "Authentication" in str(e):
        print("Check your token")
    elif "Bad request" in str(e):
        print("Invalid parameters")
    else:
        print(f"API Error: {e}")
```

## 8. Support

For support, please contact:
- Email: soporte@multiservicios-web.com.mx
- Website: https://valida-curp.com.mx/soporte

## 9. License

This project is licensed under the MIT License - see the [LICENSE](https://github.com/EdsonBurgosMsWeb/valida-curp-client-py/blob/main/LICENSE) file for details.
