#include <Servo.h>

// Definición de pines y variables globales
int sensorPin1 = A3;  // Pin analógico para el sensor de presión garra 1
int sensorPin2 = A4;  // Pin analógico para el sensor de presión garra 2
int sensorPin3 = A5;  // Pin analógico para el sensor de presión garra 3
int ledRojo = 3;
int ledVerde = 4;
int servoPin = 2;
const int triggerPin = 6;
const int echoPin = 5;
long duration;
int cm, inches;
Servo myServo;  // Crear un objeto de la clase Servo

int presion1;  // Declarar estas variables en el ámbito global
int presion2;
int presion3;

// Enumeración para definir estados
enum Estado {
  ESPERANDO,
  MOVIMIENTO_SERVO,
};

Estado estado = ESPERANDO;

// Función para medir la distancia con el sensor ultrasónico
void readUltrasonicDistance() {
  digitalWrite(triggerPin, LOW);
  delayMicroseconds(2);
  digitalWrite(triggerPin, HIGH);
  delayMicroseconds(10);
  digitalWrite(triggerPin, LOW);
  duration = pulseIn(echoPin, HIGH);
  cm = duration * 0.034 / 2;
  inches = duration * 0.0133 / 2;
  Serial.print("Distancia: ");
  Serial.print(cm);
  Serial.print("cm, ");
  Serial.print(inches);
  Serial.println("in");
}

// Función para controlar el movimiento del servomotor
void moverServo() {
  static int angle = 0;  // Ángulo del servomotor
  // Verificar la presión en los tres sensores
  if (presion1 >= 200 && presion2 >= 200 && presion3 >= 200) {
    myServo.write(angle);  // Detener el servomotor si se detecta una presión de 200 o más en cualquiera de los tres sensores
    estado = ESPERANDO;
    Serial.println("Movimiento del servomotor completado");
  } else {
    myServo.write(angle);
    angle++;
    // Reiniciar el ángulo cuando llega a 90 grados
    if (angle > 90) {
      angle = 0;
      estado = ESPERANDO;
      Serial.println("Movimiento del servomotor completado");
    }
  }
}

void setup() {
  Serial.begin(9600);
  // Configuración de pines
  pinMode(ledRojo, OUTPUT);
  pinMode(ledVerde, OUTPUT);
  pinMode(servoPin, OUTPUT);
  pinMode(triggerPin, OUTPUT);
  pinMode(echoPin, INPUT);
  pinMode(sensorPin1, INPUT);
  pinMode(sensorPin2, INPUT);
  pinMode(sensorPin3, INPUT);
  // Inicialización del servomotor
  myServo.attach(servoPin);
  myServo.write(0);  // Inicializar el servomotor en la posición 0 grados
  Serial.println("Inserte 1 si esta bien, y 0 si esta quemada la galleta");
}

void loop() {
  readUltrasonicDistance();

  // Leer valores de los sensores de presión
  presion1 = analogRead(sensorPin1);
  presion2 = analogRead(sensorPin2);
  presion3 = analogRead(sensorPin3);

  Serial.print("Sensor de presion dedo 1: ");
  Serial.println(presion1);
  Serial.print("Sensor de presion dedo 2: ");
  Serial.println(presion2);
  Serial.print("Sensor de presion dedo 3: ");
  Serial.println(presion3);

  // Realizar tareas según el estado actual
  switch (estado) {
    case ESPERANDO:
      // Leer la entrada del usuario cada 3 segundos
      if (Serial.available() > 0) {
        char input = Serial.read();
        // Verificar si la distancia es menor o igual a 20 cm
        if (cm <= 20) {
          if (input == '1') {
            digitalWrite(ledVerde, HIGH);
            digitalWrite(ledRojo, LOW);
            Serial.println("Galleta en buen estado");
          } else if (input == '0') {
            digitalWrite(ledVerde, LOW);
            digitalWrite(ledRojo, HIGH);
            Serial.println("Galleta quemada!!, iniciando movimiento del servomotor...");
            estado = MOVIMIENTO_SERVO;
          } else {
            digitalWrite(ledVerde, LOW);
            digitalWrite(ledRojo, LOW);
          }
        }
      }
      break;

    case MOVIMIENTO_SERVO:
      moverServo();
      break;
  }
}