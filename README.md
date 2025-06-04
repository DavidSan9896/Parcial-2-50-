# Parcial 2 – 50 %

Este repositorio contiene la solución al Parcial 2 de Arquitecturas de Software, calificado sobre 50 %. La entrega consta de una aplicación compuesta por cuatro servicios Docker que se comunican mediante RabbitMQ y son expuestos a través de Traefik.

## Tabla de contenido

1. [Sección 1: Conceptos teóricos](#sección-1-conceptos-teóricos)
2. [Requisitos previos](#requisitos-previos)
3. [Puesta en marcha rápida](#puesta-en-marcha-rápida)
4. [Arquitectura de la solución](#arquitectura-de-la-solución)

   1. [Implementación básica](#21-implementación-básica)
   2. [API productora de mensajes](#22-api-productora-de-mensajes)
   3. [Worker consumidor](#23-worker-consumidor)
   4. [Configuración de Traefik](#24-configuración-de-traefik)
5. [Pruebas y verificación](#pruebas-y-verificación)
6. [Autor](#autor)

---

## SECCIÓN 1: CONCEPTOS TEÓRICOS

### 1.1 RabbitMQ

* **¿Qué es RabbitMQ y cuándo se debe utilizar una cola frente a un exchange tipo fanout?**
  RabbitMQ es un nos permite el manejo de colas de los mensajes, para la comunicaccion, asi tenesmo el control por orden de llegada, debemos usar exchage tipo fanout, cuando debemos enviar el mismo mensaje a varios usuarios o consumidores en el mismo tiempo.

* **¿Qué es una Dead Letter Queue (DLQ) y cómo se configura en RabbitMQ?**
  Este es aquel que usamos para las colas que no fuereon procesadas correctamentes ya sea por errores de conexiones o rechasadas 
  Se configura estableciendo las propiedades `x-dead-letter-exchange` y opcionalmente `x-dead-letter-routing-key` en la cola original.

### 1.2 Docker y Docker Compose

* **Diferencia entre un volumen y un bind mount con ejemplos.**

  * Un **volumen** Los volumenes se usan para tener persistencia hace que los datos de los contenedores se alamcanean en una parte del sistema de ficheros el cual lo quetiona docker y solo este tiene acceso
     `/var/lib/docker/volumes`.
    Ejemplo:

    ```yaml
    volumes:
      - my_volume:/app/data
    ```
  * Un **bind mount** lo que estamos haciendo es “mapear” (montar) una parte de mi sistema de ficheros, de la que yo normalmente tengo el control, con una parte del sistema de ficheros del contenedor. Por lo tanto podemos montar tanto directorios como ficheros. De esta manera conseguimos:

Compartir ficheros entre el host y los containers.
    Ejemplo:

    ```yaml
    volumes:
      - ./datos_locales:/app/data
    ```
referecncia: https://iesgn.github.io/curso_docker_2021/sesion3/volumenes.html
* **¿Qué implica usar `network_mode: host` en un contenedor?**
  El contenedor comparte la red del host directamente,El modo host permite que el contenedor use directamente la red de la máquina virtual, de modo que Nginx puede acceder a los puertos del host (como el 80) sin pasos adicionales.
  referencia: https://labex.io/es/tutorials/docker-how-to-use-docker-compose-with-host-network-configuration-394882

### 1.3 Traefik

* **Función de Traefik en una arquitectura de microservicios.**
 Traefik es un proxy inverso y balanceador de carga adaptado a la computación en la nube mediante microservicios. este es un simplemente opera y orquesta todo los servicio que se van usar, permitiendo una conexxion, ya que intercepta las peticiones entrantes y las redirige a los servicios adecuados. A diferencia de proxys inversos configurados de forma estática

Referencia: https://picodotdev.github.io/blog-bitix/2021/09/el-proxy-inverso-traefik-caracteristicas-y-funcionalidades-que-ofrece/ 
* **¿Cómo se puede asegurar un endpoint usando certificados TLS automáticos en Traefik?**
  Traefik puede generar y renovar certificados TLS automáticamente mediante Let's Encrypt, usando los mecanismos de ACME (HTTP-01 o DNS-01). Basta con configurar el proveedor ACME y habilitar TLS en las reglas de enrutamiento usando etiquetas.

---

## Requisitos previos

* Docker ≥ 24.x
* Docker Compose ≥ v2
* Git

---

## Puesta en marcha rápida

```bash
# Clonar el repositorio
git clone <REPO_URL>
cd <NOMBRE_DEL_REPOSITORIO>

# Levantar los servicios
docker-compose up -d
```

![Servicios levantados](https://github.com/user-attachments/assets/02fad0f8-6c5f-4795-ad45-b869d7776500)

---

## Arquitectura de la solución

### 2.1 Implementación básica

El archivo `docker-compose.yml` declara los siguientes servicios:

| Servicio     | Descripción                                         |
| ------------ | --------------------------------------------------- |
| **api**      | API REST que publica mensajes en RabbitMQ           |
| **worker**   | Worker que consume mensajes y los persiste en disco |
| **rabbitmq** | Broker de mensajería                                |
| **traefik**  | Reverse proxy y balanceador de carga                |

![docker-compose.yml](https://github.com/user-attachments/assets/c28d5720-0667-434a-b86f-bb60ce771a27)

![Servicios en ejecución](https://github.com/user-attachments/assets/20ce5f49-5a9a-40a7-a8f3-e1ed963a639a)

![Logs de Docker](https://github.com/user-attachments/assets/673df600-beff-4037-875b-a0886fbbec63)

![Traefik dashboard](https://github.com/user-attachments/assets/b3706385-fe3d-4fac-9ce1-790b342ab386)

---

### 2.2 API productora de mensajes

La API ofrece el endpoint `POST /message`, protegido mediante autenticación básica, que recibe un JSON y publica su contenido en la cola `messages`.

* Usuario: **david**
* Contraseña: **9896**

**Ejemplo de invocación:**

```bash
curl -X POST "http://localhost/api/message" \
  -u david:9896 \
  -H "Content-Type: application/json" \
  -d '{"content":"Hola, esto está funcionando 😀"}'
```

![Publicación de mensaje](https://github.com/user-attachments/assets/bc3f5832-cae0-4ffd-91a9-7abbd21c9abb)

![Mensaje enviado](https://github.com/user-attachments/assets/fb3d233d-d638-4ba1-9b39-f9ec00db7b9d)

---

### 2.3 Worker consumidor

El worker escucha la cola `messages` y escribe cada mensaje recibido en el archivo `messages.log`, el cual se conserva mediante un volumen Docker.

Para visualizar el log:

```bash
docker exec -it parcial2_worker_1 cat /app/messages/messages.log
```

![Contenido de messages.log](https://github.com/user-attachments/assets/ce48e3ae-6737-4322-be84-9207cdadb009)

---

### 2.4 Configuración de Traefik

Traefik enruta las siguientes rutas:

| Ruta       | Servicio destino                          |
| ---------- | ----------------------------------------- |
| `/api`     | **api**                                   |
| `/monitor` | **rabbitmq** (interfaz de administración) |

La configuración se declara mediante etiquetas (`labels`) en `docker-compose.yml`.

![Traefik route /api](https://github.com/user-attachments/assets/f496fb15-1b77-445e-ae63-3853df43eb67)

![Etiquetas para /api](https://github.com/user-attachments/assets/9c8bbe31-e626-4f29-8df2-64376a4e9869)

![Etiquetas para /monitor](https://github.com/user-attachments/assets/ff74e138-fab3-42af-9575-6726f47e3e4a)

---

## Pruebas y verificación

1. Levanta la pila con `docker-compose up -d`.
2. Genera un mensaje con el `curl` mostrado en la sección [2.2](#22-api-productora-de-mensajes).
3. Comprueba que el mensaje aparece en `messages.log` según lo descrito en [2.3](#23-worker-consumidor).
4. Accede a:

   * `http://localhost/api` para probar el endpoint
   * `http://localhost/monitor` para la consola de RabbitMQ
   * `http://localhost:8080` para el panel de Traefik (si está habilitado)

---

## Autor

**David <Apellido>** – *Estudiante de <Universidad>*

---

> *“Los programas deben escribirse para que la gente los lea y, de paso, para que las máquinas los ejecuten.”* – Harold Abelson
