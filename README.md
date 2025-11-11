# ExamenPractico-JPRD
Examen Práctico-Juan Pablo Rovayo Delgado
## Instrucciones de instalación y configuración

1. **Clonar el repositorio**:
   ```bash
   git clone https://github.com/usuario/nombre-del-repositorio.git


2. **Instalar dependencias**:
Asegúrate de tener Python 3.x y pip instalados en tu sistema. Luego, instala las dependencias necesarias usando el archivo requirements.txt
    ```bash
    pip install -r requirements.txt

3. **Configuración de las variables de entorno**
Crea un archivo .env en la raíz del proyecto y agrega las siguientes variables:
    ```plaintext
    MYSQL_HOST=tu_host_mysql
    MYSQL_USER=tu_usuario_mysql
    MYSQL_PASSWORD=tu_contraseña_mysql
    MYSQL_DB=tu_base_de_datos_mysql
    MONGO_URI=tu_uri_mongodb


4. **Ejecución del Programa**
Una vez clonado y todo configurado, entra dentro de la carpeta raíz del proyecto y ejecuta el archivo main.py:
    ```bash
    cd EXAMENPRACTICO-JPRD
    python main.py


**Explicación de la estructura de la base de datos**
MySQL:
1. Usuarios:
    email (PK)
    username (único)
    password_hash (almacena el hash de la contraseña)

MongoDB:
1. Usuarios:
    email (único)
    username
    password_hash (almacena el hash de la contraseña)
    activo (booleano, indica si el usuario está activo)

**Decisiones de diseño tomadas**
-Autenticación y almacenamiento seguro:

    Las contraseñas de los usuarios se almacenan de manera segura utilizando bcrypt para el hash de las contraseñas.

-Base de datos dual:

    Se utilizaron MySQL para almacenar los usuarios y MongoDB como base de datos NoSQL para permitir una gestión más flexible y rápida de las sesiones de usuario.

-Manejo de sesiones:

    La sesión del usuario se guarda en una variable global usuario_logueado que se limpia cuando el usuario cierra sesión.

-Recuperación de contraseña:

    El proceso de recuperación de contraseña es simulado mediante un código de recuperación de seis dígitos, que se genera y valida manualmente.

**Dificultades encontradas y soluciones**:

- **Problema con la comparación de contraseñas en MongoDB**: 
  Inicialmente, las contraseñas no se almacenaban de forma consistente en MongoDB. Se resolvió utilizando **bcrypt** para almacenar las contraseñas de manera consistente en **MySQL** y **MongoDB**.

- **Validación de email único**:
  Cuando un usuario intentaba cambiar su **email**, había que verificar que el nuevo **email** no estuviera ya registrado en la base de datos. Esto se resolvió añadiendo una validación adicional en la función **editar perfil**.

