import cv2
import numpy as np
import time
from util import get_limits
from sklearn.metrics import accuracy_score, recall_score

yellow = [0, 255, 255]  # Amarillo en el espacio de color BGR
black = [0, 0, 0]  # Negro en el espacio de color BGR

cap = cv2.VideoCapture(0)

# Tomar una captura inicial para usar como referencia
ret, reference_frame = cap.read()
reference_frame_gray = cv2.cvtColor(reference_frame, cv2.COLOR_BGR2GRAY)

# Inicializar la variable para rastrear la detección anterior
objeto_detectado_previo = np.zeros((3, 3), dtype=bool)
verdad_conocida = np.zeros((3, 3), dtype=bool)

# Variable para controlar la impresión de resultados cada 10 segundos
start_time = time.time()

while True:
    ret, frame = cap.read()
    height, width, _ = frame.shape

    # Convertir el cuadro actual a escala de grises para comparación
    frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # Calcular la diferencia entre el cuadro actual y la imagen de referencia
    diff = cv2.absdiff(reference_frame_gray, frame_gray)

    # Umbral para determinar si hay cambios significativos
    threshold = 30
    _, threshold_diff = cv2.threshold(diff, threshold, 255, cv2.THRESH_BINARY)

    # Contar píxeles blancos en la diferencia
    pixel_count = cv2.countNonZero(threshold_diff)

    # Variable para rastrear si se ha detectado algo en la iteración actual
    algo_detectado = False

    # Si hay cambios significativos, realizar la detección de galletas quemadas
    if pixel_count > 1000:  # Ajusta este umbral según tus necesidades
        for i in range(3):
            for j in range(3):
                # Obtener la región actual
                region = frame[i * height // 3:(i + 1) * height // 3, j * width // 3:(j + 1) * width // 3]

                # Convertir la región a HSV
                hsv_region = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)

                # Definir los límites de color (amarillo)
                lower_limit, upper_limit = get_limits(color=yellow)

                # Aplicar la máscara para el amarillo
                mask_yellow = cv2.inRange(hsv_region, lower_limit, upper_limit)

                # Aplicar la máscara para el negro
                mask_black = cv2.inRange(hsv_region, np.array([0, 0, 0]), np.array([180 + 25, 255 + 25, 30 + 25]))

                # Verificar si se detecta un objeto en la región actual
                objeto_detectado_yellow = cv2.countNonZero(mask_yellow) > 0
                objeto_detectado_black = cv2.countNonZero(mask_black) > 0
                objeto_detectado = objeto_detectado_yellow or objeto_detectado_black

                # Actualizar la verdad conocida
                verdad_conocida[i, j] = objeto_detectado_black  # Establecer a True si la galleta está quemada

                # Actualizar el estado previo
                if objeto_detectado and not objeto_detectado_previo[i, j]:
                    print(f"Galleta {'quemada' if objeto_detectado_black else 'en buen estado'} en la sección ({i + 1}, {j + 1})")
                    objeto_detectado_previo[i, j] = True
                    algo_detectado = True
                elif not objeto_detectado:
                    objeto_detectado_previo[i, j] = False

                # Dibujar el cuadro de la región
                color = (0, 255, 0) if objeto_detectado_yellow else (0, 0, 255) if objeto_detectado_black else (255, 255, 255)
                frame = cv2.rectangle(frame, (j * width // 3, i * height // 3),
                                      ((j + 1) * width // 3, (i + 1) * height // 3), color, 5)

    # Calcular métricas cada 10 segundos
    if algo_detectado and time.time() - start_time >= 10:
        # Convertir a un arreglo unidimensional para comparar con las detecciones del modelo
        verdad_conocida_unidimensional = verdad_conocida.flatten()
        objeto_detectado_previo_unidimensional = objeto_detectado_previo.flatten()

        # Calcular y mostrar métricas
        accuracy = accuracy_score(verdad_conocida_unidimensional, objeto_detectado_previo_unidimensional)
        recall = recall_score(verdad_conocida_unidimensional, objeto_detectado_previo_unidimensional)

        print("Matriz de verdad conocida:")
        print(verdad_conocida.astype(int))
        print("Matriz de detección del modelo:")
        print(objeto_detectado_previo.astype(int))
        print(f"Accuracy: {accuracy:.2f}")
        print(f"Recall: {recall:.2f}")

        # Reiniciar el temporizador y actualizar la imagen de referencia
        start_time = time.time()
        reference_frame_gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    cv2.imshow('frame', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
