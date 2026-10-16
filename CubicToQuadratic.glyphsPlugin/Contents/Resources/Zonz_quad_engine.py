# -*- coding: utf-8 -*-
# Copyright 2026 Zonz
# -*- coding: utf-8 -*-
"""Localized UI and expected errors; unknown errors retain API diagnostics."""
TRANSLATIONS = {
  "keep_curve_tangent": {
    "en": "Maintain smooth curve joins",
    "zh-Hans": "维持平滑的曲线连接处",
    "zh-Hant": "維持平滑的曲線連接處",
    "ja": "曲線同士の滑らかな接続を維持",
    "ko": "곡선 사이의 매끄러운 연결 유지",
    "de": "Glatte Kurvenverbindungen erhalten",
    "fr": "Maintenir les raccords lisses entre courbes",
    "es": "Mantener uniones suaves entre curvas",
    "it": "Mantieni raccordi morbidi tra curve",
    "pt": "Manter junções suaves entre curvas",
    "ru": "Сохранять плавные соединения кривых"
},
  "title": {
    "en": "Convert to Compact Quadratic Curves",
    "zh-Hans": "转换为精简的二次曲线",
    "zh-Hant": "轉換為精簡的二次曲線",
    "ja": "簡潔な二次曲線に変換",
    "ko": "간결한 2차 곡선으로 변환",
    "de": "In kompakte quadratische Kurven umwandeln",
    "fr": "Convertir en courbes quadratiques compactes",
    "es": "Convertir a curvas cuadráticas compactas",
    "it": "Converti in curve quadratiche compatte",
    "pt": "Converter em curvas quadráticas compactas",
    "ru": "Преобразовать в компактные квадратичные кривые"
  },
  "settings": {
    "en": "Convert to Compact Quadratic Curves Settings⋯",
    "zh-Hans": "转换为精简的二次曲线设置⋯",
    "zh-Hant": "轉換為精簡的二次曲線設定⋯",
    "ja": "簡潔な二次曲線に変換の設定⋯",
    "ko": "간결한 2차 곡선으로 변환 설정⋯",
    "de": "Einstellungen: In kompakte quadratische Kurven umwandeln⋯",
    "fr": "Réglages : Convertir en courbes quadratiques compactes⋯",
    "es": "Ajustes: Convertir a curvas cuadráticas compactas⋯",
    "it": "Impostazioni: Converti in curve quadratiche compatte⋯",
    "pt": "Configurações: Converter em curvas quadráticas compactas⋯",
    "ru": "Настройки: Преобразовать в компактные квадратичные кривые⋯"
  },
  "midpoint": {
    "en": "Insert points between controls",
    "zh-Hans": "在控制点间加入锚点",
    "zh-Hant": "在控制點間加入錨點",
    "ja": "制御点の間にノードを追加",
    "ko": "제어점 사이에 노드 추가",
    "de": "Knoten zwischen Kontrollpunkten einfügen",
    "fr": "Insérer des nœuds entre les contrôles",
    "es": "Insertar nodos entre controles",
    "it": "Inserisci nodi tra i controlli",
    "pt": "Inserir nós entre controles",
    "ru": "Добавить узлы между контрольными точками"
  },
  "cancel": {
    "en": "Cancel",
    "zh-Hans": "取消",
    "zh-Hant": "取消",
    "ja": "キャンセル",
    "ko": "취소",
    "de": "Abbrechen",
    "fr": "Annuler",
    "es": "Cancelar",
    "it": "Annulla",
    "pt": "Cancelar",
    "ru": "Отмена"
  },
  "ok": {
    "en": "OK",
    "zh-Hans": "好",
    "zh-Hant": "好",
    "ja": "OK",
    "ko": "확인",
    "de": "OK",
    "fr": "OK",
    "es": "Aceptar",
    "it": "OK",
    "pt": "OK",
    "ru": "ОК"
  },
  "preparing": {
    "en": "Preparing…",
    "zh-Hans": "正在准备……",
    "zh-Hant": "正在準備……",
    "ja": "準備中…",
    "ko": "준비 중…",
    "de": "Vorbereitung…",
    "fr": "Préparation…",
    "es": "Preparando…",
    "it": "Preparazione…",
    "pt": "Preparando…",
    "ru": "Подготовка…"
  },
  "invalid": {
    "en": "The outline fitting tolerance must be a finite number greater than zero.",
    "zh-Hans": "轮廓拟合容差必须是大于零的有限数值。",
    "zh-Hant": "輪廓擬合容差必須是大於零的有限數值。",
    "ja": "輪郭偏差の上限は0より大きい有限の数値にしてください。",
    "ko": "윤곽 편차 상한은 0보다 큰 유한한 숫자여야 합니다.",
    "de": "Die Konturabweichung muss eine endliche Zahl größer als null sein.",
    "fr": "L’écart maximal doit être un nombre fini supérieur à zéro.",
    "es": "La desviación debe ser un número finito mayor que cero.",
    "it": "Lo scostamento deve essere un numero finito maggiore di zero.",
    "pt": "O desvio deve ser um número finito maior que zero.",
    "ru": "Отклонение должно быть конечным числом больше нуля."
  },
  "missing_master": {
    "en": "Missing master layer: ",
    "zh-Hans": "缺少主版图层：",
    "zh-Hant": "缺少主版圖層：",
    "ja": "マスターレイヤーがありません：",
    "ko": "마스터 레이어 없음: ",
    "de": "Fehlende Masterebene: ",
    "fr": "Calque maître manquant : ",
    "es": "Falta la capa maestra: ",
    "it": "Livello master mancante: ",
    "pt": "Camada mestre ausente: ",
    "ru": "Отсутствует слой мастера: "
  },
  "no_master": {
    "en": "No editable masters in this font.",
    "zh-Hans": "字体没有可编辑主版",
    "zh-Hant": "字型沒有可編輯主版",
    "ja": "編集可能なマスターがありません。",
    "ko": "편집 가능한 마스터가 없습니다.",
    "de": "Keine bearbeitbaren Master vorhanden.",
    "fr": "Aucun maître modifiable.",
    "es": "No hay maestros editables.",
    "it": "Nessun master modificabile.",
    "pt": "Não há mestres editáveis.",
    "ru": "Нет редактируемых мастеров."
  },
  "incompatible": {
    "en": "Glyphs reports incompatible masters; this glyph was skipped.",
    "zh-Hans": "Glyphs 报告主版不兼容，未作转换",
    "zh-Hant": "Glyphs 回報主版不相容，未作轉換",
    "ja": "Glyphsがマスターの非互換を報告したため、スキップしました。",
    "ko": "Glyphs가 마스터 호환 불가를 보고하여 건너뛰었습니다.",
    "de": "Glyphs meldet inkompatible Master; die Glyphe wurde übersprungen.",
    "fr": "Glyphs signale des maîtres incompatibles ; le glyphe a été ignoré.",
    "es": "Glyphs indica maestros incompatibles; se omitió el glifo.",
    "it": "Glyphs segnala master incompatibili; il glifo è stato saltato.",
    "pt": "Glyphs indica mestres incompatíveis; o glifo foi ignorado.",
    "ru": "Glyphs сообщает о несовместимых мастерах; глиф пропущен."
  },
  "structure": {
    "en": "Master or special-layer path, node, component or anchor structures differ.",
    "zh-Hans": "主版或特殊图层的轮廓、节点、组件或锚点结构不同",
    "zh-Hant": "主版或特殊圖層的輪廓、節點、組件或錨點結構不同",
    "ja": "マスターまたは特殊レイヤーのパス・ノード・コンポーネント・アンカー構造が異なります。",
    "ko": "마스터 또는 특수 레이어의 윤곽, 노드, 구성 요소, 앵커 구조가 다릅니다.",
    "de": "Pfad-, Knoten-, Komponenten- oder Ankerstrukturen der Ebenen unterscheiden sich.",
    "fr": "Les structures de tracés, nœuds, composants ou ancres des calques diffèrent.",
    "es": "Las estructuras de trazados, nodos, componentes o anclas de las capas difieren.",
    "it": "Le strutture di tracciati, nodi, componenti o ancore dei livelli differiscono.",
    "pt": "As estruturas de contornos, nós, componentes ou âncoras das camadas diferem.",
    "ru": "Структуры контуров, узлов, компонентов или якорей слоёв различаются."
  },
  "unsupported": {
    "en": "Unsupported path node arrangement.",
    "zh-Hans": "存在不支持的轮廓节点排列",
    "zh-Hant": "存在不支援的輪廓節點排列",
    "ja": "未対応のパスノード配列です。",
    "ko": "지원하지 않는 윤곽 노드 배열입니다.",
    "de": "Nicht unterstützte Knotenanordnung.",
    "fr": "Disposition des nœuds non prise en charge.",
    "es": "Disposición de nodos no compatible.",
    "it": "Disposizione dei nodi non supportata.",
    "pt": "Disposição de nós não suportada.",
    "ru": "Неподдерживаемый порядок узлов."
  },
  "invalid_nodes": {
    "en": "The generated quadratic node structure is invalid.",
    "zh-Hans": "生成的二次曲线节点结构无效",
    "zh-Hant": "產生的二次曲線節點結構無效",
    "ja": "生成された二次曲線のノード構造が無効です。",
    "ko": "생성된 2차 곡선의 노드 구조가 유효하지 않습니다.",
    "de": "Ungültige erzeugte Knotenstruktur.",
    "fr": "Structure des nœuds quadratiques générée invalide.",
    "es": "Estructura de nodos cuadráticos generada inválida.",
    "it": "Struttura dei nodi quadratici generata non valida.",
    "pt": "Estrutura de nós quadráticos gerada inválida.",
    "ru": "Неверная структура созданных квадратичных узлов."
  },
  "left_font": {
    "en": "The glyph no longer belongs to the original font.",
    "zh-Hans": "字形已离开原字体",
    "zh-Hant": "字形已離開原字型",
    "ja": "字形が元のフォントに属していません。",
    "ko": "글리프가 원래 폰트에 속하지 않습니다.",
    "de": "Die Glyphe gehört nicht mehr zur ursprünglichen Schrift.",
    "fr": "Le glyphe n’appartient plus à la police d’origine.",
    "es": "El glifo ya no pertenece a la fuente original.",
    "it": "Il glifo non appartiene più al font originale.",
    "pt": "O glifo não pertence mais à fonte original.",
    "ru": "Глиф больше не принадлежит исходному шрифту."
  },
  "changed_structure": {
    "en": "Glyph structure changed during preparation; conversion cancelled: ",
    "zh-Hans": "准备期间字形结构已改变，已取消转换：",
    "zh-Hant": "準備期間字形結構已改變，已取消轉換：",
    "ja": "準備中に字形構造が変更されたため中止しました：",
    "ko": "준비 중 글리프 구조가 바뀌어 변환을 취소함: ",
    "de": "Glyphenstruktur während der Vorbereitung geändert; abgebrochen: ",
    "fr": "Structure modifiée pendant la préparation ; conversion annulée : ",
    "es": "Estructura modificada durante la preparación; conversión cancelada: ",
    "it": "Struttura modificata durante la preparazione; conversione annullata: ",
    "pt": "Estrutura alterada durante a preparação; conversão cancelada: ",
    "ru": "Структура изменена при подготовке; преобразование отменено: "
  },
  "edited": {
    "en": "Path edited during preparation; conversion cancelled: ",
    "zh-Hans": "准备期间轮廓已被编辑，已取消转换：",
    "zh-Hant": "準備期間輪廓已被編輯，已取消轉換：",
    "ja": "準備中にパスが編集されたため中止しました：",
    "ko": "준비 중 윤곽이 편집되어 변환을 취소함: ",
    "de": "Pfad während der Vorbereitung bearbeitet; abgebrochen: ",
    "fr": "Tracé modifié pendant la préparation ; conversion annulée : ",
    "es": "Trazado editado durante la preparación; conversión cancelada: ",
    "it": "Tracciato modificato durante la preparazione; conversione annullata: ",
    "pt": "Contorno editado durante a preparação; conversão cancelada: ",
    "ru": "Контур изменён при подготовке; преобразование отменено: "
  },
  "changed_layers": {
    "en": "Master or special layers changed during preparation; conversion cancelled.",
    "zh-Hans": "准备期间主版或特殊图层已改变，已取消转换",
    "zh-Hant": "準備期間主版或特殊圖層已改變，已取消轉換",
    "ja": "準備中にマスターまたは特殊レイヤーが変更されたため中止しました。",
    "ko": "준비 중 마스터 또는 특수 레이어가 바뀌어 변환을 취소했습니다.",
    "de": "Ebenen während der Vorbereitung geändert; abgebrochen.",
    "fr": "Calques modifiés pendant la préparation ; conversion annulée.",
    "es": "Capas modificadas durante la preparación; conversión cancelada.",
    "it": "Livelli modificati durante la preparazione; conversione annullata.",
    "pt": "Camadas alteradas durante a preparação; conversão cancelada.",
    "ru": "Слои изменены при подготовке; преобразование отменено."
  },
  "hint_changed": {
    "en": "Hints now reference replaced handles; conversion cancelled.",
    "zh-Hans": "提示指令引用了将被替换的手柄节点，已取消转换",
    "zh-Hant": "提示指令引用了將被替換的手柄節點，已取消轉換",
    "ja": "ヒントが置換予定のハンドルを参照しているため中止しました。",
    "ko": "힌트가 교체될 핸들을 참조하여 변환을 취소했습니다.",
    "de": "Hints verweisen auf zu ersetzende Griffe; abgebrochen.",
    "fr": "Des hints référencent les poignées à remplacer ; conversion annulée.",
    "es": "Los hints referencian manejadores que se reemplazarían; conversión cancelada.",
    "it": "Gli hint fanno riferimento a maniglie da sostituire; conversione annullata.",
    "pt": "Os hints referenciam alças que seriam substituídas; conversão cancelada.",
    "ru": "Хинты ссылаются на заменяемые ручки; преобразование отменено."
  },
  "post_compat": {
    "en": "Master compatibility check failed after conversion: ",
    "zh-Hans": "转换后主版兼容性检查未通过：",
    "zh-Hant": "轉換後主版相容性檢查未通過：",
    "ja": "変換後のマスター互換性検査に失敗しました：",
    "ko": "변환 후 마스터 호환성 확인 실패: ",
    "de": "Master-Kompatibilitätsprüfung nach Umwandlung fehlgeschlagen: ",
    "fr": "Échec du contrôle de compatibilité après conversion : ",
    "es": "Falló la comprobación de compatibilidad tras la conversión: ",
    "it": "Verifica di compatibilità fallita dopo la conversione: ",
    "pt": "Falha na verificação de compatibilidade após a conversão: ",
    "ru": "Проверка совместимости после преобразования не пройдена: "
  },
  "rollback": {
    "en": "; rollback incomplete: ",
    "zh-Hans": "；回滚未完成：",
    "zh-Hant": "；復原未完成：",
    "ja": "；復元が完了しませんでした：",
    "ko": "; 롤백 미완료: ",
    "de": "; Wiederherstellung unvollständig: ",
    "fr": " ; restauration incomplète : ",
    "es": "; restauración incompleta: ",
    "it": "; ripristino incompleto: ",
    "pt": "; restauração incompleta: ",
    "ru": "; откат не завершён: "
  },
  "count_mismatch": {
    "en": "Corresponding masters have different control-point counts.",
    "zh-Hans": "对应主版的控制点数量不同",
    "zh-Hant": "對應主版的控制點數量不同",
    "ja": "対応するマスターの制御点数が異なります。",
    "ko": "대응 마스터의 제어점 수가 다릅니다.",
    "de": "Kontrollpunktanzahl der Master stimmt nicht überein.",
    "fr": "Le nombre de points de contrôle diffère entre les maîtres.",
    "es": "El número de controles difiere entre maestros.",
    "it": "Il numero di punti di controllo differisce tra i master.",
    "pt": "A quantidade de controles difere entre os mestres.",
    "ru": "Количество контрольных точек мастеров различается."
  },
  "changed_font": {
    "en": "The active font changed; conversion cancelled.",
    "zh-Hans": "当前字体已改变，已取消转换",
    "zh-Hant": "目前字型已改變，已取消轉換",
    "ja": "使用中のフォントが変更されたため中止しました。",
    "ko": "활성 폰트가 바뀌어 변환을 취소했습니다.",
    "de": "Aktive Schrift geändert; Umwandlung abgebrochen.",
    "fr": "Police active modifiée ; conversion annulée.",
    "es": "Fuente activa modificada; conversión cancelada.",
    "it": "Font attivo cambiato; conversione annullata.",
    "pt": "Fonte ativa alterada; conversão cancelada.",
    "ru": "Активный шрифт изменён; преобразование отменено."
  },
  "no_font": {
    "en": "Open a font first.",
    "zh-Hans": "请先打开一个字体",
    "zh-Hant": "請先開啟一個字型",
    "ja": "先にフォントを開いてください。",
    "ko": "먼저 폰트를 여세요.",
    "de": "Zuerst eine Schrift öffnen.",
    "fr": "Ouvrez d’abord une police.",
    "es": "Abra primero una fuente.",
    "it": "Apri prima un font.",
    "pt": "Abra uma fonte primeiro.",
    "ru": "Сначала откройте шрифт."
  },
  "native": {
    "en": "Glyphs native quadratic preflight failed; no font changes were made.",
    "zh-Hans": "Glyphs 原生二次曲线预检未通过，未修改字体。",
    "zh-Hant": "Glyphs 原生二次曲線預檢未通過，未修改字型。",
    "ja": "Glyphsの二次曲線事前検査に失敗しました。フォントは変更されていません。",
    "ko": "Glyphs 네이티브 2차 곡선 사전 확인에 실패했으며 폰트는 변경되지 않았습니다.",
    "de": "Native Kurvenprüfung fehlgeschlagen; Schrift unverändert.",
    "fr": "Échec du contrôle natif des courbes ; police inchangée.",
    "es": "Falló la comprobación nativa; no se modificó la fuente.",
    "it": "Controllo nativo fallito; font non modificato.",
    "pt": "Falha na verificação nativa; fonte não modificada.",
    "ru": "Проверка нативных кривых не пройдена; шрифт не изменён."
  },
  "deviation": {
    "en": "Outline fitting tolerance",
    "zh-Hans": "轮廓拟合容差",
    "zh-Hant": "輪廓擬合容差",
    "ja": "輪郭近似の許容誤差",
    "ko": "윤곽 피팅 허용 오차",
    "de": "Toleranz der Konturanpassung",
    "fr": "Tolérance d’ajustement du contour",
    "es": "Tolerancia de ajuste del contorno",
    "it": "Tolleranza di adattamento del contorno",
    "pt": "Tolerância de ajuste do contorno",
    "ru": "Допуск аппроксимации контура"
  },
  "max_controls": {
    "en": "Maximum control points",
    "zh-Hans": "控制点数量上限",
    "zh-Hant": "控制點數量上限",
    "ja": "制御点数の上限",
    "ko": "제어점 수 상한",
    "de": "Maximale Anzahl der Kontrollpunkte",
    "fr": "Nombre maximal de points de contrôle",
    "es": "Número máximo de puntos de control",
    "it": "Numero massimo di punti di controllo",
    "pt": "Número máximo de pontos de controle",
    "ru": "Максимальное число контрольных точек"
  },
  "invalid_count": {
    "en": "The maximum control-point count must be a positive integer.",
    "zh-Hans": "控制点数量上限必须是正整数。",
    "zh-Hant": "控制點數量上限必須是正整數。",
    "ja": "制御点数の上限は正の整数にしてください。",
    "ko": "제어점 수 상한은 양의 정수여야 합니다.",
    "de": "Die maximale Kontrollpunktzahl muss eine positive ganze Zahl sein.",
    "fr": "Le nombre maximal de points de contrôle doit être un entier positif.",
    "es": "El número máximo de puntos de control debe ser un entero positivo.",
    "it": "Il numero massimo di punti di controllo deve essere un intero positivo.",
    "pt": "O número máximo de pontos de controle deve ser um inteiro positivo.",
    "ru": "Максимальное число контрольных точек должно быть положительным целым."
  },
  "merge_curves": {
    "en": "Try merging smoothly joined curves",
    "zh-Hans": "尝试合并平滑连接的曲线",
    "zh-Hant": "嘗試合併平滑連接的曲線",
    "ja": "滑らかにつながる曲線の結合を試す",
    "ko": "부드럽게 연결된 곡선 병합 시도",
    "de": "Glatt verbundene Kurven versuchsweise zusammenführen",
    "fr": "Essayer de fusionner les courbes jointes sans cassure",
    "es": "Intentar unir curvas conectadas suavemente",
    "it": "Prova a unire curve collegate senza spigoli",
    "pt": "Tentar unir curvas conectadas suavemente",
    "ru": "Попробовать объединить плавно соединённые кривые"
  },
  "center_limit": {
    "en": "Centering range for controls near the chord",
    "zh-Hans": "尝试居中贴线控制点范围",
    "zh-Hant": "嘗試居中貼線控制點範圍",
    "ja": "両端点を結ぶ線に近い制御点の中央寄せ範囲",
    "ko": "양 끝점의 연결선 근처 제어점 중앙 배치 범위",
    "de": "Zentrierbereich für Kontrollpunkte nahe der Sehne",
    "fr": "Plage de centrage des contrôles proches de la corde",
    "es": "Rango de centrado de controles próximos a la cuerda",
    "it": "Intervallo di centratura dei controlli vicini alla corda",
    "pt": "Faixa de centralização dos controles próximos da corda",
    "ru": "Диапазон центрирования точек вблизи хорды"
  },
  "integer_coords": {
    "en": "Fit using integer coordinates",
    "zh-Hans": "以整数座标转换",
    "zh-Hant": "以整數座標轉換",
    "ja": "整数座標で変換",
    "ko": "정수 좌표로 변환",
    "de": "Mit ganzzahligen Koordinaten anpassen",
    "fr": "Ajuster en coordonnées entières",
    "es": "Ajustar con coordenadas enteras",
    "it": "Adatta con coordinate intere",
    "pt": "Ajustar com coordenadas inteiras",
    "ru": "Подгонять в целочисленных координатах"
  },
  "invalid_center": {
    "en": "The centering range must be finite and non-negative.",
    "zh-Hans": "尝试居中贴线控制点范围必须是大于或等于零的有限数值。",
    "zh-Hant": "嘗試居中貼線控制點範圍必須是大於或等於零的有限數值。",
    "ja": "中央寄せの上限は0以上の有限数にしてください。",
    "ko": "중앙 배치 상한은 0 이상의 유한한 수여야 합니다.",
    "de": "Die Zentrierungsgrenze muss endlich und nicht negativ sein.",
    "fr": "Le seuil de centrage doit être fini et positif ou nul.",
    "es": "El umbral de centrado debe ser finito y no negativo.",
    "it": "La soglia di centratura deve essere finita e non negativa.",
    "pt": "O limite de centralização deve ser finito e não negativo.",
    "ru": "Порог центрирования должен быть конечным и неотрицательным."
  },
  "invalid_upm": {
    "en": "The font UPM must be finite and positive.",
    "zh-Hans": "字体 UPM 必须是大于零的有限数值。",
    "zh-Hant": "字型 UPM 必須是大於零的有限數值。",
    "ja": "フォントのUPMは正の有限数にしてください。",
    "ko": "폰트 UPM은 양의 유한한 수여야 합니다.",
    "de": "Der UPM-Wert muss endlich und positiv sein.",
    "fr": "La valeur UPM doit être finie et strictement positive.",
    "es": "El UPM debe ser finito y positivo.",
    "it": "Il valore UPM deve essere finito e positivo.",
    "pt": "O UPM deve ser finito e positivo.",
    "ru": "UPM должен быть конечным положительным числом."
  },
  "changed_upm": {
    "en": "The font UPM changed; conversion cancelled.",
    "zh-Hans": "准备期间字体 UPM 已改变，已取消转换。",
    "zh-Hant": "準備期間字型 UPM 已改變，已取消轉換。",
    "ja": "準備中にフォントのUPMが変わったため中止しました。",
    "ko": "준비 중 폰트 UPM이 바뀌어 변환을 취소했습니다.",
    "de": "UPM-Wert während der Vorbereitung geändert; abgebrochen.",
    "fr": "La valeur UPM a changé ; conversion annulée.",
    "es": "El UPM cambió; conversión cancelada.",
    "it": "Il valore UPM è cambiato; conversione annullata.",
    "pt": "O UPM mudou; conversão cancelada.",
    "ru": "UPM изменился; преобразование отменено."
  },
  "angle_limit": {
    "en": "Angle tolerance for smooth joins",
    "zh-Hans": "视为平滑连接的角度容差",
    "zh-Hant": "視為平滑連接的角度容差",
    "ja": "滑らかな接続とみなす角度の許容差",
    "ko": "부드러운 연결로 간주할 각도 허용 오차",
    "de": "Winkeltoleranz für glatte Verbindungen",
    "fr": "Tolérance angulaire des jonctions lisses",
    "es": "Tolerancia angular para uniones suaves",
    "it": "Tolleranza angolare per giunzioni morbide",
    "pt": "Tolerância angular para junções suaves",
    "ru": "Угловой допуск для плавных соединений"
  },
  "keep_line_tangent": {
    "en": "Maintain smooth straight-line joins",
    "zh-Hans": "维持平滑的直线连接处",
    "zh-Hant": "維持平滑的直線連接處",
    "ja": "直線との滑らかな接続を維持",
    "ko": "직선과의 부드러운 연결 유지",
    "de": "Glatte Anschlüsse an Geraden erhalten",
    "fr": "Maintenir les jonctions lisses avec les droites",
    "es": "Mantener uniones suaves con rectas",
    "it": "Mantieni le giunzioni morbide con le rette",
    "pt": "Manter junções suaves com retas",
    "ru": "Сохранять плавные соединения с прямыми"
  },
  "invalid_angle": {
    "en": "The connection angle tolerance must be between 0° and 180°.",
    "zh-Hans": "视为平滑连接的角度容差必须是 0° 至 180° 之间的有限数值。",
    "zh-Hant": "視為平滑連接的角度容差必須是 0° 至 180° 之間的有限數值。",
    "ja": "接続角度の許容差は0°から180°の有限数にしてください。",
    "ko": "연결 각도 허용 오차는 0°에서 180° 사이의 유한한 수여야 합니다.",
    "de": "Die Winkeltoleranz muss zwischen 0° und 180° liegen.",
    "fr": "La tolérance angulaire doit être comprise entre 0° et 180°.",
    "es": "La tolerancia angular debe estar entre 0° y 180°.",
    "it": "La tolleranza angolare deve essere tra 0° e 180°.",
    "pt": "A tolerância angular deve estar entre 0° e 180°.",
    "ru": "Допуск угла должен быть от 0° до 180°."
  },
  "tangent_conflict": {
    "en": "The control-count and coordinate limits cannot preserve the required connection tangents.",
    "zh-Hans": "无法在当前控制点与座标限制下保持连接切线。",
    "zh-Hant": "無法在目前控制點與座標限制下保持連接切線。",
    "ja": "現在の制御点数と座標の制限では接続の接線を維持できません。",
    "ko": "현재 제어점 수와 좌표 제한으로 연결 접선을 유지할 수 없습니다.",
    "de": "Mit diesen Punkt- und Koordinatengrenzen lassen sich die Tangenten nicht erhalten.",
    "fr": "Les limites de points et de coordonnées empêchent de préserver les tangentes.",
    "es": "Los límites de puntos y coordenadas impiden conservar las tangentes.",
    "it": "I limiti di punti e coordinate impediscono di mantenere le tangenti.",
    "pt": "Os limites de pontos e coordenadas impedem preservar as tangentes.",
    "ru": "Ограничения точек и координат не позволяют сохранить касательные."
  },

}

def tr(key, language=None, **values):
    translations=dict(TRANSLATIONS[key])
    translations.update({'zh':translations['zh-Hans'], 'zh-CN':translations['zh-Hans'],
                         'zh-SG':translations['zh-Hans'], 'zh-TW':translations['zh-Hant'],
                         'zh-HK':translations['zh-Hant'], 'zh-MO':translations['zh-Hant']})
    if language is not None:
        language=language.replace('_','-')
        while language not in translations and '-' in language:language=language.rsplit('-',1)[0]
        text=translations.get(language,translations['en'])
    else:
        try:
            from GlyphsApp import Glyphs
            text=Glyphs.localize(translations)
        except ImportError:text=translations['en']
    return text.format(**values)

# -*- coding: utf-8 -*-
"""Validated settings; deviation and distances are units on the UPM 1000 scale."""
import math
import struct

PREFERENCE_PREFIX='com.Zonz.CubicToQuadratic.'
DEFAULT_SETTINGS=dict(deviation=1.0,max_controls=3,add_midpoint=False,merge_curves=True,center_limit=7.0,integer_coords=True,angle_limit=5.0,keep_line_tangent=True,keep_curve_tangent=True)

def validated_settings(deviation=1.0,max_controls=2,add_midpoint=False,merge_curves=False,center_limit=0.0,integer_coords=False,angle_limit=2.0,keep_line_tangent=False,keep_curve_tangent=False):
    try:
        deviation=float(deviation)
        if deviation<=0 or not math.isfinite(deviation):raise ValueError()
    except (ValueError,TypeError,OverflowError):raise ValueError(tr('invalid'))
    try:
        center_limit=float(center_limit)
        if center_limit<0 or not math.isfinite(center_limit):raise ValueError()
    except (ValueError,TypeError,OverflowError):raise ValueError(tr('invalid_center'))
    try:
        angle_limit=float(angle_limit)
        if not math.isfinite(angle_limit) or not 0<=angle_limit<=180:raise ValueError()
    except (ValueError,TypeError,OverflowError):raise ValueError(tr('invalid_angle'))
    try:
        if isinstance(max_controls,bool):raise ValueError()
        count=int(max_controls)
        if count<1 or (not isinstance(max_controls,(int,str)) and count!=max_controls):raise ValueError()
    except (ValueError,TypeError,OverflowError):raise ValueError(tr('invalid_count'))
    return dict(deviation=deviation,max_controls=count,add_midpoint=bool(add_midpoint),
                merge_curves=bool(merge_curves),
                center_limit=center_limit,integer_coords=bool(integer_coords),angle_limit=angle_limit,keep_line_tangent=bool(keep_line_tangent),keep_curve_tangent=bool(keep_curve_tangent))

def stored(app,key):
    try:return app.defaults[PREFERENCE_PREFIX+key]
    except KeyError:return None

def decimal_preference(value):
    if not isinstance(value,float) or not math.isfinite(value):return value
    try:
        packed=struct.pack('f',value)
        if struct.unpack('f',packed)[0]!=value:return value
        for precision in range(1,10):
            text=format(value,'.'+str(precision)+'g')
            if struct.pack('f',float(text))==packed:return text
    except (OverflowError,struct.error):pass
    return value

def encoded_settings(values):
    return {PREFERENCE_PREFIX+k:str(v) if k in ('deviation','max_controls','center_limit','angle_limit') else v for k,v in values.items()}

def load_settings(app):
    values={k:stored(app,k) for k in DEFAULT_SETTINGS}
    if values['deviation'] is not None:values['deviation']=decimal_preference(values['deviation'])
    values={k:DEFAULT_SETTINGS[k] if v is None else v for k,v in values.items()}
    try:values=validated_settings(**values)
    except ValueError:values=dict(DEFAULT_SETTINGS)
    # Persist validated text values instead of binary32 numeric preferences.
    for key,value in encoded_settings(values).items():app.defaults[key]=value
    return values

def save_settings(app,**values):
    settings=validated_settings(**values)
    for key,value in encoded_settings(settings).items():app.defaults[key]=value
    return settings

# -*- coding: utf-8 -*-
"""Bezier primitives and algebraic seeds; geometric fitting is in fast_fit."""
import math
VERSION = '1.0'

def dot(a, b):
    return (a.conjugate() * b).real

def cross(a, b):
    return (a.conjugate() * b).imag

def cubic(p, t):
    u = 1.0 - t
    return u*u*u*p[0] + 3*u*u*t*p[1] + 3*u*t*t*p[2] + t*t*t*p[3]

def quadratic(q, t):
    u = 1.0 - t
    return u*u*q[0] + 2*u*t*q[1] + t*t*q[2]

def split(p, t=0.5):
    a, b, c = [(1-t)*p[i]+t*p[i+1] for i in range(3)]
    d, e = (1-t)*a+t*b, (1-t)*b+t*c
    m = (1-t)*d+t*e
    return (p[0], a, d, m), (m, e, c, p[3])

def single_l2(p):
    return (p[0], (3*p[1]+3*p[2]-p[0]-p[3])/4.0, p[3])

def solve(a, b):
    """Small positive-definite systems, with partial pivoting."""
    n = len(b)
    m = [list(row)+[v] for row, v in zip(a, b)]
    scale = max(abs(v) for row in a for v in row)
    for col in range(n):
        pivot = max(range(col, n), key=lambda j: abs(m[j][col]))
        if abs(m[pivot][col]) <= 1e-13*max(scale, 1e-300):
            raise ValueError('Singular fitting system')
        m[col], m[pivot] = m[pivot], m[col]
        div = m[col][col]
        m[col] = [v/div for v in m[col]]
        for j in range(n):
            if j != col:
                f = m[j][col]
                m[j] = [x-f*y for x, y in zip(m[j], m[col])]
    return [row[-1] for row in m]

def tangent(p, end=False):
    anchor = p[-1] if end else p[0]
    seq = (p[2], p[1], p[0]) if end else (p[1], p[2], p[3])
    for point in seq:
        v = point-anchor
        if abs(v) > 1e-12:
            return v/abs(v)
    return None

def weights(p, power=2.0):
    lengths = (abs(p[1]-p[0]), abs(p[2]-p[3]))
    top = max(lengths)
    return tuple((v/top)**power if top and v else 0.0 for v in lengths)

def single_weighted(p, strength=1.0, power=2.0):
    q = single_l2(p)[1]
    mat = [[1.0, 0.0], [0.0, 1.0]]
    rhs = [q.real, q.imag]
    for end, w in zip((False, True), weights(p, power)):
        u = tangent(p, end)
        if u is None or not w:
            continue
        n = 1j*u
        anchor = p[3] if end else p[0]
        v = (n.real, n.imag)
        amount = strength*w
        for i in range(2):
            rhs[i] += amount*v[i]*dot(n, anchor)
            for j in range(2):
                mat[i][j] += amount*v[i]*v[j]
    x, y = solve(mat, rhs)
    return (p[0], complex(x, y), p[3])

def intersection(p):
    u, v = tangent(p), tangent(p, True)
    if u is None or v is None:
        return None
    den = cross(u, v)
    if abs(den) < 1e-10:
        return None
    d = p[3]-p[0]
    a, b = cross(d, v)/den, cross(d, u)/den
    if a <= 1e-12 or b <= 1e-12:
        return None
    return (p[0], p[0]+a*u, p[3])

def pair_basis(s, half):
    """Q = base + b0*q0 + b1*q1, M=(q0+q1)/2."""
    if half == 0:
        return (2*s-1.5*s*s, 0.5*s*s, (1-s)**2, 0.0)
    return (0.5*(1-s)**2, 0.5*(1-s)**2+2*s*(1-s), 0.0, s*s)

def pair_l2(p):
    a, b = split(p)
    return [single_l2(a), single_l2(b)]

def angle(a, b):
    if abs(a) <= 1e-12 or abs(b) <= 1e-12:
        return None
    return math.degrees(math.atan2(cross(a, b), dot(a, b)))

def diagnostics(p, parts):
    return (angle(p[1]-p[0], parts[0][1]-parts[0][0]),
            angle(p[2]-p[3], parts[-1][1]-parts[-1][2]))

# -*- coding: utf-8 -*-
"""Exact nearest-segment queries, accelerated by a small AABB tree."""
import math


class SegmentIndex:
    def __init__(self, line):
        self.edges=[]
        for a,b in zip(line,line[1:]):
            v=b-a;den=v.real*v.real+v.imag*v.imag
            self.edges.append((a,v,1.0/den if den else 0.0))
        def build(ids):
            xs=[x for i in ids for x in (line[i].real,line[i+1].real)]
            ys=[y for i in ids for y in (line[i].imag,line[i+1].imag)]
            box=(min(xs),min(ys),max(xs),max(ys))
            if len(ids)<=6:return (box,ids,None)
            axis=0 if box[2]-box[0]>=box[3]-box[1] else 1
            ids.sort(key=lambda i:(line[i].real+line[i+1].real) if axis==0
                     else (line[i].imag+line[i+1].imag))
            mid=len(ids)//2
            return (box,build(ids[:mid]),build(ids[mid:]))
        self.root=build(list(range(len(self.edges)))) if self.edges else None

    def nearest(self,z):
        if self.root is None:return float('inf'),0,0.0
        x,y=z.real,z.imag;best=float('inf');index=0;local=0.0
        def lower(node):
            a,b,c,d=node[0]
            dx=a-x if x<a else (x-c if x>c else 0.0)
            dy=b-y if y<b else (y-d if y>d else 0.0)
            return dx*dx+dy*dy
        stack=[(0.0,self.root)]
        while stack:
            bound,node=stack.pop()
            if bound>best:continue
            if node[2] is None:
                for i in node[1]:
                    a,v,inverse=self.edges[i]
                    dx=x-a.real;dy=y-a.imag
                    t=(dx*v.real+dy*v.imag)*inverse
                    t=0.0 if t<0 else (1.0 if t>1 else t)
                    dx-=t*v.real;dy-=t*v.imag;d=dx*dx+dy*dy
                    if d<best or (d==best and i<index):best,index,local=d,i,t
            else:
                left,right=node[1:];a,b=lower(left),lower(right)
                if a<b:stack.extend(((b,right),(a,left)))
                else:stack.extend(((a,left),(b,right)))
        return math.sqrt(best),index,local


class IndexedLine(list):
    def __init__(self,values):
        super().__init__(values)
        self.segment_index=SegmentIndex(self)

# -*- coding: utf-8 -*-
"""Degree <= 3 roots on [0,1], using quadratic knots and bracketed Newton."""
import math


def polynomial_roots_unit(coeff):
    scale=max(map(abs,coeff))
    if not scale:return []
    c=[v/scale for v in coeff]
    while len(c)>1 and abs(c[-1])<1e-14:c.pop()
    def inside(values):
        return sorted(set(max(0.0,min(1.0,v)) for v in values if -1e-12<=v<=1+1e-12))
    if len(c)==1:return []
    if len(c)==2:return inside([-c[0]/c[1]])
    if len(c)==3:
        a,b,d=c[2],c[1],c[0];disc=b*b-4*a*d
        if disc<0:return []
        q=-.5*(b+math.copysign(math.sqrt(disc),b))
        return inside([q/a,d/q] if q else [-b/(2*a)])
    if len(c)!=4:raise ValueError('Only degree <= 3 is used by this fitter')
    d,b,a,h=c
    value=lambda t:((h*t+a)*t+b)*t+d
    derivative=lambda t:(3*h*t+2*a)*t+b
    knots=[0.0]+polynomial_roots_unit([b,2*a,3*h])+[1.0]
    roots=[t for t in knots if abs(value(t))<1e-11]
    for lo,hi in zip(knots,knots[1:]):
        flo,fhi=value(lo),value(hi)
        if flo*fhi>=0:continue
        t=(lo+hi)/2
        for _ in range(26):
            f=value(t)
            if f==0:break
            if flo*f<=0:hi=t
            else:lo=t;flo=f
            der=derivative(t)
            step=f/der if der else float('inf')
            proposal=t-step
            if abs(step)<2e-14 and lo<=proposal<=hi:
                t=proposal;break
            if hi-lo<2e-13:t=(lo+hi)/2;break
            t=proposal if lo<proposal<hi and abs(step)<.8*(hi-lo) else (lo+hi)/2
        else:
            # Difficult nearly multiple roots retain a reliable bracket fallback.
            for _ in range(38):
                t=(lo+hi)/2;f=value(t)
                if flo*f<=0:hi=t
                else:lo=t;flo=f
            t=(lo+hi)/2
        roots.append(t)
    roots.sort();result=[]
    for t in roots:
        if not result or abs(t-result[-1])>1e-9:result.append(t)
    return result

# -*- coding: utf-8 -*-
"""Geometric fitting with implicit quadratic joins; pure Python 3.

Optimization uses a sampled objective. Acceptance uses bidirectional
polyline Hausdorff bounds plus certified Bezier flattening bounds.
"""
import math
import heapq


def point_segment(z, a, b):
    v = b-a
    length2 = dot(v,v)
    if not length2:
        return abs(z-a)
    t = max(0.0,min(1.0,dot(z-a,v)/length2))
    return abs(z-a-t*v)


def nearest_polyline(z, line):
    if hasattr(line,'segment_index'):
        d,i,t=line.segment_index.nearest(z)
        return d,i
    best, index = float('inf'), 0
    for i in range(len(line)-1):
        d = point_segment(z,line[i],line[i+1])
        if d < best:
            best,index = d,i
    return best,index


def flatten(points, tolerance):
    """Polyline within tolerance in Hausdorff distance (exact arithmetic).

    Convex-hull distance to the finite chord bounds curve-to-chord error;
    continuous projection between endpoints bounds chord-to-curve error.
    """
    out = [points[0]]
    stack = [(tuple(points),0)]
    worst = 0.0
    while stack:
        p,depth = stack.pop()
        flatness = max(point_segment(v,p[0],p[-1]) for v in p[1:-1])
        if flatness <= tolerance or depth >= 24:
            out.append(p[-1]);worst = max(worst,flatness)
            continue
        levels=[p]
        while len(levels[-1])>1:
            levels.append(tuple((a+b)/2 for a,b in zip(levels[-1],levels[-1][1:])))
        a = tuple(row[0] for row in levels)
        b = tuple(row[-1] for row in reversed(levels))
        stack.append((b,depth+1));stack.append((a,depth+1))
    return IndexedLine(out),worst


def arc_samples(line, count):
    lengths=[abs(b-a) for a,b in zip(line,line[1:])]
    total=sum(lengths)
    if not total:
        return [line[0]]*count
    result=[];edge=0;before=0.0
    for i in range(count):
        target=total*i/(count-1)
        while edge<len(lengths)-1 and before+lengths[edge]<target:
            before+=lengths[edge];edge+=1
        t=(target-before)/lengths[edge] if lengths[edge] else 0.0
        result.append(line[edge]+min(1.0,max(0.0,t))*(line[edge+1]-line[edge]))
    return result


def nearest_quadratic(z,q):
    a=q[0]-z;b=2*(q[1]-q[0]);c=q[0]-2*q[1]+q[2]
    coeff=(dot(a,b),dot(b,b)+2*dot(a,c),3*dot(b,c),2*dot(c,c))
    candidates=[0.0,1.0]+polynomial_roots_unit(coeff)
    t=min(candidates,key=lambda t:abs(a+b*t+c*t*t))
    return abs(a+b*t+c*t*t),t


def geometric_bounds(p,parts,tolerance=1.0,accuracy=None,reject_above=None,source_cache=None,source_curves=None):
    """Conservative continuous bidirectional Hausdorff interval.

    Max iterations/depth only leave a looser upper bound, never an assumed
    sampled guarantee. Includes a scale-related floating point allowance.
    """
    accuracy=accuracy if accuracy is not None else max(.002,tolerance*.02)
    delta=accuracy/8.0
    bounds_points=tuple(p) if source_curves is None else tuple(z for q in source_curves for z in q)
    key=(tuple(p) if source_curves is None else tuple(map(tuple,source_curves)),delta)
    if source_cache is not None and key in source_cache:
        original,ea=source_cache[key]
    else:
        if source_curves is None:original,ea=flatten(p,delta)
        else:
            points=[];ea=0.0
            for curve in source_curves:
                line,error=flatten(curve,delta);points.extend(line if not points else line[1:]);ea=max(ea,error)
            original=IndexedLine(points)
        if source_cache is not None:
            if len(source_cache)>=8:source_cache.pop(next(iter(source_cache)))
            source_cache[key]=(original,ea)
    fitted=[];eb=0.0
    for q in parts:
        line,e=flatten(q,delta)
        fitted.extend(line if not fitted else line[1:]);eb=max(eb,e)
    fitted=IndexedLine(fitted)
    allowance=max([1.0]+list(map(abs,bounds_points))+[abs(v) for q in parts for v in q])*1e-10
    hull_upper=max([abs(v-p[0]) for v in bounds_points]+[abs(v-p[0]) for q in parts for v in q])+allowance
    heap=[];lower=0.0;serial=0
    def record(a,b,da,db,ia,ib,target,depth):
        nonlocal lower,serial
        lower=max(lower,da,db)
        candidates={ia,ib}
        upper=min(max(point_segment(a,target[j],target[j+1]),
                      point_segment(b,target[j],target[j+1])) for j in candidates)
        upper=min(upper,(da+db+abs(b-a))/2.0)
        heapq.heappush(heap,(-upper,serial,a,b,da,db,ia,ib,target,depth));serial+=1
    for source,target in ((original,fitted),(fitted,original)):
        distances=[]
        for z in source:
            d,i=nearest_polyline(z,target);distances.append((d,i))
            lower=max(lower,d)
            if reject_above is not None and lower-ea-eb-allowance>reject_above:
                return lower-ea-eb-allowance,hull_upper
        for i,(a,b) in enumerate(zip(source,source[1:])):
            da,ia=distances[i];db,ib=distances[i+1]
            record(a,b,da,db,ia,ib,target,0)
    for _ in range(10000):
        if reject_above is not None and lower-ea-eb-allowance>reject_above:
            break
        if not heap or -heap[0][0]-lower<=accuracy/2.0:
            break
        item=heapq.heappop(heap)
        neg,ix,a,b,da,db,ia,ib,target,depth=item
        if depth>=24:
            heapq.heappush(heap,item);break
        m=(a+b)/2;dm,im=nearest_polyline(m,target)
        record(a,m,da,dm,ia,im,target,depth+1)
        record(m,b,dm,db,im,ib,target,depth+1)
    allowance=max([1.0]+list(map(abs,bounds_points))+[abs(v) for q in parts for v in q])*1e-10
    return max(0.0,lower-ea-eb-allowance),max(lower,-heap[0][0] if heap else lower)+ea+eb+allowance


def nelder_mead(objective,initial,step=.025,iterations=180):
    """Small derivative-free local optimizer; no global-optimum claim."""
    dim=len(initial)
    vertices=[list(initial)]
    for i in range(dim):
        v=list(initial);v[i]+=step;vertices.append(v)
    scored=[(objective(v),v) for v in vertices]
    for _ in range(iterations):
        scored.sort(key=lambda r:r[0])
        if max(abs(a-b) for _,v in scored[1:] for a,b in zip(v,scored[0][1]))<2e-6:
            break
        centre=[sum(v[i] for _,v in scored[:-1])/dim for i in range(dim)]
        worst=scored[-1][1]
        reflected=[2*a-b for a,b in zip(centre,worst)];fr=objective(reflected)
        if fr<scored[0][0]:
            expanded=[3*a-2*b for a,b in zip(centre,worst)];fe=objective(expanded)
            scored[-1]=(fe,expanded) if fe<fr else (fr,reflected)
        elif fr<scored[-2][0]:
            scored[-1]=(fr,reflected)
        else:
            outside=fr<scored[-1][0]
            contracted=[(a+b)/2 for a,b in zip(centre,reflected if outside else worst)]
            fc=objective(contracted)
            if fc<(fr if outside else scored[-1][0]):scored[-1]=(fc,contracted)
            else:
                best=scored[0][1]
                scored=[scored[0]]+[(objective(v2),v2) for _,v in scored[1:]
                    for v2 in [[(a+b)/2 for a,b in zip(best,v)]]]
    return min(scored,key=lambda r:r[0])


def make_context(p,flatness=2e-5):
    line,_=flatten(p,flatness)
    return line,arc_samples(line,41)


def sampled_objective(parts,context,maximum=True):
    line,samples=context
    forward=[min(nearest_quadratic(z,q)[0] for q in parts) for z in samples]
    reverse=[]
    for q in parts:
        for i in range(25):reverse.append(nearest_polyline(quadratic(q,i/24.0),line)[0])
    if maximum:return max(forward+reverse)
    return sum(d*d for d in forward)/len(forward)+sum(d*d for d in reverse)/len(reverse)


def optimize_one(p,context,maximum=True):
    seeds=[single_l2(p)[1],single_weighted(p)[1]]
    q=intersection(p)
    if q is not None and abs(q[1]-p[0])<25:seeds.append(q[1])
    # Pick the best sampled starts; preserve the unmodified candidates too.
    ranked=sorted(seeds,key=lambda z:sampled_objective([(p[0],z,p[3])],context,maximum))
    best=[]
    for q in ranked[:2]:
        objective=lambda xy:sampled_objective([(p[0],complex(*xy),p[3])],context,maximum)
        score,xy=nelder_mead(objective,[q.real,q.imag],iterations=140)
        best.append((score,(p[0],complex(*xy),p[3])))
    for q in ranked:best.append((sampled_objective([(p[0],q,p[3])],context,maximum),(p[0],q,p[3])))
    return min(best,key=lambda r:r[0])[1]



# -*- coding: utf-8 -*-
"""Unconstrained geometric fitting, arc-length weights and multiple starts.

No endpoint tangent constraints. Coordinates are normalized before search.
"""
import math


def numeric_cache():
    """Reuse normalized fitting solutions across conversions."""
    import sys,types
    name='_Zonz_compact_quadratic_numeric_cache'
    if name not in sys.modules:
        module=types.ModuleType(name);module.values={};sys.modules[name]=module
    return sys.modules[name].values


def polyline_parameterization(p,tolerance=1e-6):
    stack=[(p,0.0,1.0,0)];points=[p[0]];times=[0.0]
    while stack:
        q,a,b,depth=stack.pop()
        if max(point_segment(z,q[0],q[-1]) for z in q[1:-1])<=tolerance or depth>=20:
            points.append(q[-1]);times.append(b)
        else:
            left,right=split(q);m=(a+b)/2
            stack.append((right,m,b,depth+1));stack.append((left,a,m,depth+1))
    return points,times


class Context:
    def __init__(self,p,count=65,reverse_count=25,geometry=None):
        self.p=p
        self.reverse_count=reverse_count
        if geometry is None:
            self.line,self.times=polyline_parameterization(p)
            self.index=SegmentIndex(self.line)
        else:
            self.line,self.times,self.index=geometry
        self.geometry=(self.line,self.times,self.index)
        lengths=[abs(b-a) for a,b in zip(self.line,self.line[1:])]
        self.samples=[];total=sum(lengths);edge=0;before=0.0
        for i in range(count):
            target=total*i/(count-1)
            while edge<len(lengths)-1 and before+lengths[edge]<target:
                before+=lengths[edge];edge+=1
            local=(target-before)/lengths[edge] if lengths[edge] else 0.0
            t=self.times[edge]+local*(self.times[edge+1]-self.times[edge])
            weight=.5 if i==0 or i==count-1 else 1.0
            self.samples.append((cubic(p,t),weight/(count-1)))

    def tangent(self,t):
        p=self.p;u=1-t
        return 3*(u*u*(p[1]-p[0])+2*u*t*(p[2]-p[1])+t*t*(p[3]-p[2]))

    def interior(self,t):
        return 1e-7<t<1-1e-7

    def nearest(self,z):
        best,index,part=self.index.nearest(z)
        # Refine the closest polyline location on the original cubic itself.
        a=self.times[max(0,index-1)];b=self.times[min(len(self.times)-1,index+2)]
        t=self.times[index]+part*(self.times[index+1]-self.times[index])
        p=self.p
        for _ in range(5):
            u=1-t
            pos=cubic(p,t)
            der=3*(u*u*(p[1]-p[0])+2*u*t*(p[2]-p[1])+t*t*(p[3]-p[2]))
            second=6*(u*(p[2]-2*p[1]+p[0])+t*(p[3]-2*p[2]+p[1]))
            denominator=dot(der,der)+dot(pos-z,second)
            if denominator<=1e-15:break
            proposed=max(a,min(b,t-dot(pos-z,der)/denominator))
            if abs(proposed-t)<1e-10:break
            t=proposed
        candidates=[0.0,1.0,t,self.times[index]+part*(self.times[index+1]-self.times[index])]
        t=min(candidates,key=lambda v:abs(cubic(p,v)-z))
        return cubic(p,t),t


def unpack(p,x):
    controls=[complex(x[i],x[i+1]) for i in range(0,len(x),2)]
    joins=[p[0]]+[(a+b)/2 for a,b in zip(controls,controls[1:])]+[p[3]]
    return [(joins[i],q,joins[i+1]) for i,q in enumerate(controls)]


def pack(parts):
    return [v for q in parts for v in (q[1].real,q[1].imag)]


def basis(s,segment,count):
    if count==1:
        value=2*s*(1-s)
        return [complex(value,0),complex(0,value)]
    if count==2:
        a,b,_,_=pair_basis(s,segment)
        return [complex(a,0),complex(0,a),complex(b,0),complex(0,b)]
    weights=[0.0]*count;u=1-s
    weights[segment]=2*u*s
    if segment>0:
        weights[segment-1]+=u*u/2;weights[segment]+=u*u/2
    if segment<count-1:
        weights[segment]+=s*s/2;weights[segment+1]+=s*s/2
    return [v for w in weights for v in (complex(w,0),complex(0,w))]


def sample_rows(parts,context,reverse_count=None):
    """Residual/Jacobian rows with balanced, arc-length-aware weights."""
    reverse_count=reverse_count or context.reverse_count
    count=len(parts);rows=[];norms=[]
    for z,weight in context.samples:
        candidates=[nearest_quadratic(z,q)+(i,) for i,q in enumerate(parts)]
        distance,s,i=min(candidates,key=lambda v:v[0]);q=parts[i]
        value=quadratic(q,s);der=2*((1-s)*(q[1]-q[0])+s*(q[2]-q[1]))
        jac=basis(s,i,count);difference=value-z
        if abs(der)>1e-12 and 1e-7<s<1-1e-7:
            normal=1j*der/abs(der)
            rows.append((dot(difference,normal),[dot(v,normal) for v in jac],weight*.5))
        else:
            rows.append((difference.real,[v.real for v in jac],weight*.5))
            rows.append((difference.imag,[v.imag for v in jac],weight*.5))
        norms.append((distance,weight*.5))
    reverse=[];length=0.0
    for i,q in enumerate(parts):
        for k in range(reverse_count):
            s=k/(reverse_count-1)
            position=quadratic(q,s)
            der=2*((1-s)*(q[1]-q[0])+s*(q[2]-q[1]))
            weight=abs(der)*(.5 if k==0 or k==reverse_count-1 else 1)/(reverse_count-1)
            target,t=context.nearest(position)
            tangent=context.tangent(t)
            jac=basis(s,i,count);difference=position-target
            reverse.append((difference,tangent,jac,weight,t));length+=weight
    length=max(length,1e-15)
    for difference,tangent,jac,weight,t in reverse:
        weight=weight/length*.5
        if abs(tangent)>1e-12 and context.interior(t):
            normal=1j*tangent/abs(tangent)
            rows.append((dot(difference,normal),[dot(v,normal) for v in jac],weight))
        else:
            rows.append((difference.real,[v.real for v in jac],weight))
            rows.append((difference.imag,[v.imag for v in jac],weight))
        norms.append((abs(difference),weight))
    return rows,norms


def sample_norms(parts,context,reverse_count=None):
    """Identical distance weights to sample_rows; omit unused Jacobians."""
    reverse_count=reverse_count or context.reverse_count
    norms=[]
    for z,weight in context.samples:
        distance=min(nearest_quadratic(z,q)[0] for q in parts)
        norms.append((distance,weight*.5))
    reverse=[];length=0.0
    for q in parts:
        for k in range(reverse_count):
            s=k/(reverse_count-1)
            position=quadratic(q,s)
            der=2*((1-s)*(q[1]-q[0])+s*(q[2]-q[1]))
            weight=abs(der)*(.5 if k==0 or k==reverse_count-1 else 1)/(reverse_count-1)
            target,t=context.nearest(position)
            reverse.append((abs(position-target),weight));length+=weight
    length=max(length,1e-15)
    norms.extend((d,w/length*.5) for d,w in reverse)
    return norms


def score_norms(norms,power=2):
    if power=='max':return max(d for d,w in norms)
    return sum(w*d**power for d,w in norms)**(1.0/power)


def refine_lm(p,x,context,power=2,iterations=25):
    """Normal-distance Gauss-Newton/LM; accept only improved true objectives."""
    x=list(x);damping=1e-4
    rows,norms=sample_rows(unpack(p,x),context)
    score=score_norms(norms,power)
    for _ in range(iterations):
        dim=len(x);matrix=[[0.0]*dim for _ in range(dim)];rhs=[0.0]*dim
        largest=max([abs(r) for r,j,w in rows]+[1e-12])
        for r,jac,weight in rows:
            # Relative IRLS weights avoid tiny fourth-power normal matrices.
            weight*=max(abs(r)/largest,.001)**(power-2)
            for i in range(dim):
                rhs[i]-=weight*jac[i]*r
                for j in range(dim):matrix[i][j]+=weight*jac[i]*jac[j]
        for i in range(dim):matrix[i][i]+=damping*max(matrix[i][i],1e-9)
        try:step=solve(matrix,rhs)
        except ValueError:break
        maximum=max(map(abs,step))
        if maximum<2e-8:break
        if maximum>.2:step=[v*.2/maximum for v in step]
        proposed=[a+b for a,b in zip(x,step)]
        if max(map(abs,proposed))>20:damping*=10;continue
        newrows,newnorms=sample_rows(unpack(p,proposed),context)
        newscore=score_norms(newnorms,power)
        if newscore<score:
            improvement=score-newscore
            x,rows,norms,score=proposed,newrows,newnorms,newscore
            damping=max(1e-9,damping*.3)
            if improvement<1e-10:break
        else:
            damping*=10
            if damping>1e8:break
    return x,score


def pair_seeds(p,one):
    seeds=[pack(pair_l2(p))]
    a=(one[0]+one[1])/2;b=(one[1]+one[2])/2;m=(a+b)/2
    seeds.append(pack([(p[0],a,m),(m,b,p[3])]))
    for t in [.15,.3,.5,.7,.85]:
        left,right=split(p,t)
        # Non-half subdivision is a source of starting positions only.
        # Its fitted controls always use their midpoint as the actual join.
        seeds.append(pack([single_l2(left),single_l2(right)]))
        centre=cubic(p,t);u=1-t
        direction=3*(u*u*(p[1]-p[0])+2*u*t*(p[2]-p[1])+t*t*(p[3]-p[2]))
        if abs(direction)>1e-10:
            span=(abs(centre-p[0])+abs(p[3]-centre))/4
            direction=direction/abs(direction)*span
            seeds.append([centre.real-direction.real,centre.imag-direction.imag,
                          centre.real+direction.real,centre.imag+direction.imag])
    # Diverse midpoint/span combinations avoid starting in the same basin.
    result=[]
    for x in seeds:
        if all(max(abs(a-b) for a,b in zip(x,y))>1e-7 for y in result):result.append(x)
    return result


def choose_diverse(scored,count):
    scored=sorted(scored,key=lambda r:r[0]);chosen=[scored[0]];remaining=scored[1:]
    while remaining and len(chosen)<count:
        # Good score matters, but retain geometrically different starts.
        eligible=remaining[:max(5,count*2)]
        pick=max(eligible,key=lambda r:min(sum((a-b)**2 for a,b in zip(r[1],c[1])) for c in chosen))
        chosen.append(pick);remaining.remove(pick)
    return chosen


# -*- coding: utf-8 -*-
"""Geometric fitting of quadratic chains with implicit, smooth midpoint joins."""
import bisect

def subdivision_seed(p,times):
    remaining=p;before=0.0;parts=[]
    for end in times[1:-1]:
        left,remaining=split(remaining,(end-before)/(1-before))
        parts.append(single_l2(left));before=end
    parts.append(single_l2(remaining))
    return pack(parts)

def least_squares_seed(p,times):
    """Fit control positions together; endpoints stay fixed."""
    count=len(times)-1;matrix=[[0.0]*count for _ in range(count)];rhs=[0j]*count
    for segment in range(count):
        for j in range(9):
            s=j/8;u=1-s;t=times[segment]*(1-s)+times[segment+1]*s
            weights=[v.real for v in basis(s,segment,count)[::2]]
            target=cubic(p,t)
            if segment==0:target-=u*u*p[0]
            if segment==count-1:target-=s*s*p[3]
            weight=(times[segment+1]-times[segment])*(.5 if j in (0,8) else 1)
            for a,wa in enumerate(weights):
                rhs[a]+=weight*wa*target
                for b,wb in enumerate(weights):matrix[a][b]+=weight*wa*wb
    real=solve(matrix,[z.real for z in rhs]);imag=solve(matrix,[z.imag for z in rhs])
    return [v for a,b in zip(real,imag) for v in (a,b)]

def arc_times(context,count):
    lengths=[abs(b-a) for a,b in zip(context.line,context.line[1:])]
    cumulative=[0.0]
    for length in lengths:cumulative.append(cumulative[-1]+length)
    if cumulative[-1]<1e-15:return [i/count for i in range(count+1)]
    times=[0.0]
    for j in range(1,count):
        target=cumulative[-1]*j/count
        i=min(len(lengths)-1,bisect.bisect_right(cumulative,target)-1)
        local=(target-cumulative[i])/lengths[i] if lengths[i] else 0
        times.append(context.times[i]+local*(context.times[i+1]-context.times[i]))
    return times+[1.0]

def optimize_chain(p,count,geometry=None):
    """Three inexpensive seeds; simultaneous control optimization."""
    context=Context(p,count=max(65,12*count+1),reverse_count=17,geometry=geometry)
    uniform=[i/count for i in range(count+1)];by_arc=arc_times(context,count)
    seeds=[subdivision_seed(p,uniform),subdivision_seed(p,by_arc)]
    try:seeds.append(least_squares_seed(p,uniform))
    except ValueError:pass
    objective=lambda x:score_norms(sample_norms(unpack(p,x),context))
    candidates=sorted((objective(x),x) for x in seeds)
    for _,x in candidates[:2]:
        y,score=refine_lm(p,x,context,iterations=14)
        candidates.append((score,y))
    fine=Context(p,count=max(97,16*count+1),reverse_count=25,geometry=context.geometry)
    final=lambda x:score_norms(sample_norms(unpack(p,x),fine))
    score,best=min(((final(x),x) for _,x in candidates),key=lambda r:r[0])
    improved,value=refine_lm(p,best,fine,iterations=5)
    if value<score:best=improved
    return unpack(p,best),fine

# -*- coding: utf-8 -*-
"""Oriented tangent gates with exact or grid-cell endpoint ray constraints."""
import math
from fractions import Fraction

class TangentConflict(ValueError):
    def __init__(self):super().__init__(tr('tangent_conflict'))

def cross2(a,b):return a.real*b.imag-a.imag*b.real

def aligned(a,b,degrees):
    if abs(a)<1e-12 or abs(b)<1e-12:return False
    return abs(math.degrees(math.atan2(cross2(a,b),dot(a,b))))<=degrees+1e-9

def smooth_join(a,b,degrees):return aligned(a[3]-a[2],b[1]-b[0],degrees)

def primitive_direction(direction,step):
    x=direction.real/step;y=direction.imag/step
    fx=Fraction(x).limit_denominator(1000000);fy=Fraction(y).limit_denominator(1000000)
    denominator=fx.denominator*fy.denominator//math.gcd(fx.denominator,fy.denominator)
    ix=fx.numerator*(denominator//fx.denominator);iy=fy.numerator*(denominator//fy.denominator)
    divisor=math.gcd(ix,iy)
    if not divisor:raise TangentConflict()
    move=complex(ix//divisor,iy//divisor)*step
    if abs(cross2(move,direction))>1e-9*abs(move)*abs(direction):raise TangentConflict()
    return move

def on_ray(z,ray,step=0.0):
    if ray is None:return True
    a,d=ray;distance=z-a;length=abs(d)
    if not length:return False
    if not step:return dot(distance,d)/length>1e-10 and abs(cross2(distance,d))/length<=1e-7
    if dot(distance,d)/length<=1e-10:return False
    low=0.0;high=float('inf');half=step/2+step*1e-9
    for offset,direction in ((distance.real,d.real/length),(distance.imag,d.imag/length)):
        if abs(direction)<1e-15:
            if abs(offset)>half:return False
        else:
            bounds=sorted(((offset-half)/direction,(offset+half)/direction))
            low=max(low,bounds[0]);high=min(high,bounds[1])
    return high>=low

def lattice_ray(z,ray,step):
    a,d=ray;unit=d/abs(d)
    base=z if on_ray(z,ray,step) else a+unit*max(step/2,dot(z-a,unit))
    base=complex(round(base.real/step)*step,round(base.imag/step)*step)
    candidates=[base+complex(x,y)*step for x in (-1,0,1) for y in (-1,0,1)]
    candidates=[p for p in candidates if on_ray(p,ray,step)]
    if not candidates:raise TangentConflict()
    return min(candidates,key=lambda p:(abs(p-z),abs(cross2(p-a,unit)),p.real,p.imag))

def project_controls(controls,tangents=None,step=0.0):
    if not tangents or not any(tangents):return list(controls)
    result=list(controls);left,right=tangents
    if step:
        if len(result)==1 and left is not None and right is not None:
            z=result[0];bases=[z,lattice_ray(z,left,step),lattice_ray(z,right,step)]
            try:bases.extend(project_controls(result,tangents))
            except TangentConflict:pass
            candidates={complex(round(b.real/step)+x,round(b.imag/step)+y)*step
                        for b in bases for x in (-1,0,1) for y in (-1,0,1)}
            valid=[p for p in candidates if on_ray(p,left,step) and on_ray(p,right,step)]
            if not valid:raise TangentConflict()
            return [min(valid,key=lambda p:(abs(p-z),p.real,p.imag))]
        for index,ray in ((0,left),(len(result)-1,right)):
            if ray is not None:result[index]=lattice_ray(result[index],ray,step)
        return result
    if len(result)==1 and left is not None and right is not None:
        a,u=left;b,v=right;den=cross2(u,v)
        if abs(den)>1e-12*abs(u)*abs(v):
            z=a+u*(cross2(b-a,v)/den)
            if not on_ray(z,left) or not on_ray(z,right):raise TangentConflict()
            return [z]
        if abs(cross2(b-a,u))>1e-8*max(1.0,abs(u)):raise TangentConflict()
        unit=u/abs(u);low=1e-10;bound=dot(b-a,unit)
        if dot(u,v)<0:high=bound-1e-10
        else:low=max(low,bound+1e-10);high=float('inf')
        if low>high:raise TangentConflict()
        z=a+unit*max(low,min(high,dot(result[0]-a,unit)))
        if not on_ray(z,right):raise TangentConflict()
        return [z]
    for index,ray in ((0,left),(len(result)-1,right)):
        if ray is None:continue
        a,d=ray;unit=d/abs(d)
        result[index]=a+unit*max(1e-9,dot(result[index]-a,unit))
    return result

def optimize_constrained(controls,tangents,origin,scale,objective,cancel):
    controls=project_controls(controls,tangents)
    if len(controls)==1 and all(tangents):return controls
    rays={i:r for i,r in ((0,tangents[0]),(len(controls)-1,tangents[1])) if r is not None}
    initial=[]
    for i,z in enumerate(controls):
        if i in rays:
            a,d=rays[i];initial.append(dot(z-a,d/abs(d))/scale)
        else:initial.extend(((z-origin).real/scale,(z-origin).imag/scale))
    def decode(values):
        result=[];k=0
        for i in range(len(controls)):
            if i in rays:
                a,d=rays[i];result.append(a+d/abs(d)*max(1e-10,values[k])*scale);k+=1
            else:result.append(origin+complex(values[k],values[k+1])*scale);k+=2
        return result
    def score(values):cancel();return objective(decode(values))
    before=score(initial);after,values=nelder_mead(score,initial,step=.015,iterations=120)
    return decode(values) if after<before else controls

# -*- coding: utf-8 -*-
"""Optional tangent/lattice fitting and separately accepted one-control centering."""
import math
from concurrent.futures import CancelledError

def grid_point(z,step):return complex(round(z.real/step)*step,round(z.imag/step)*step)

def control_parts(start,end,controls,step=0.0,explicit=False):
    joins=[start]+[(a+b)/2 for a,b in zip(controls,controls[1:])]+[end]
    if step and explicit:joins[1:-1]=[grid_point(z,step) for z in joins[1:-1]]
    return [(joins[i],q,joins[i+1]) for i,q in enumerate(controls)]

def center_parts(curves,parts,tolerance,center_limit,integer_step=0.0,tangents=None,cancel=None):
    if not center_limit or len(parts)!=1:return parts
    def check():
        if cancel is not None and cancel():raise CancelledError()
    check();start,q,end=parts[0];chord=end-start
    if abs(chord)<1e-12:return parts
    direction=chord/abs(chord);middle=(start+end)/2
    offset=dot(q-middle,direction);signed_height=dot(q-start,1j*direction);height=abs(signed_height)
    if height>center_limit+max(1.0,height,center_limit)*1e-12 or abs(offset)<1e-9:return parts
    target=q-direction*offset;cache={};tangents=tangents or (None,None)
    def acceptable(control):
        check()
        if any(not on_ray(control,ray,integer_step) for ray in tangents):return False
        bounds=geometric_bounds(curves[0],[(start,control,end)],tolerance,
            accuracy=min(max(.002,tolerance*.02),tolerance*.1),reject_above=tolerance,
            source_cache=cache,source_curves=curves if len(curves)>1 else None)
        return bounds[1]<=tolerance
    if not acceptable(q):return parts
    if acceptable(target):desired=target
    else:
        low=0.0;high=1.0
        for _ in range(26):
            if (high-low)*abs(offset)<1e-6:break
            mid=(low+high)/2
            if acceptable(q+(target-q)*mid):low=mid
            else:high=mid
        desired=q+(target-q)*low
    if not integer_step:return [(start,desired,end)]
    candidates={q}
    # Include exact-height lattice motion where it exists, plus nearby quantized motion.
    try:
        move=primitive_direction(chord,integer_step)
        k=round(dot(desired-q,move)/abs(move)**2)
        candidates.update(grid_point(q+j*move,integer_step) for j in (k-1,k,k+1))
    except TangentConflict:pass
    for fraction in (1.0,.9,.75,.5,.25,0.0):
        base=grid_point(q+(desired-q)*fraction,integer_step)
        candidates.update(base+complex(x,y)*integer_step for x in (-1,0,1) for y in (-1,0,1))
    quantum=integer_step/math.sqrt(2)+1e-9
    def key(z):return (abs(dot(z-middle,direction)),abs(dot(z-start,1j*direction)-signed_height),abs(z-desired),z.real,z.imag)
    for z in sorted(candidates,key=key):
        if abs(dot(z-middle,direction))>=abs(offset)-1e-9:continue
        new_height=dot(z-start,1j*direction)
        if abs(new_height-signed_height)>quantum or new_height*signed_height<-1e-12:continue
        if acceptable(z):return [(start,z,end)]
    return parts

def adjust_parts(curves,parts,tolerance,center_limit=0.0,integer_step=0.0,explicit=False,context_factory=None,cancel=None,tangents=None):
    constrained=bool(tangents and any(tangents))
    if not integer_step and not constrained:return center_parts(curves,parts,tolerance,center_limit,cancel=cancel)
    def check():
        if cancel is not None and cancel():raise CancelledError()
    check();start,end=parts[0][0],parts[-1][-1];origin=start
    scale=max([abs(z-origin) for p in curves for z in p]+[abs(z-origin) for q in parts for z in q]+[1e-9])
    normal=tuple(tuple((z-origin)/scale for z in p) for p in curves);context=context_factory(normal);memo={}
    def objective(values):
        key=tuple(values)
        if key not in memo:
            proposed=control_parts(start,end,values,integer_step,explicit)
            normalized=[tuple((z-origin)/scale for z in q) for q in proposed]
            memo[key]=score_norms(sample_norms(normalized,context))
        return memo[key]
    controls=[q[1] for q in parts]
    if constrained:
        try:controls=optimize_constrained(controls,tangents,origin,scale,objective,check)
        except TangentConflict:
            if not integer_step:raise
            controls=project_controls(controls,tangents,integer_step)
    if integer_step:
        controls=[grid_point(z,integer_step) for z in controls]
        controls=project_controls(controls,tangents,integer_step);score=objective(controls)
        for _ in range(16):
            changed=False
            for i in range(len(controls)):
                check();best=controls;best_score=score
                directions=[complex(x,y)*integer_step for x,y in ((-1,0),(1,0),(0,-1),(0,1),(-1,-1),(-1,1),(1,-1),(1,1))]
                for delta in directions:
                    candidate=list(controls);candidate[i]=grid_point(candidate[i]+delta,integer_step)
                    try:candidate=project_controls(candidate,tangents,integer_step)
                    except TangentConflict:continue
                    value=objective(candidate)
                    if value<best_score-1e-13:best_score=value;best=candidate
                if best!=controls:controls=best;score=best_score;changed=True
            if not changed:break
    parts=control_parts(start,end,controls,integer_step,explicit)
    return center_parts(curves,parts,tolerance,center_limit,integer_step,tangents,cancel)

# -*- coding: utf-8 -*-
"""Production geometric fitting; masters share a minimal acceptable control count."""
import math
from concurrent.futures import CancelledError

def optimize_pair(p,geometry=None):
    context=Context(p,count=33,reverse_count=17,geometry=geometry)
    seeds=pair_seeds(p,single_l2(p))
    objective=lambda x:score_norms(sample_norms(unpack(p,x),context),2)
    ranked=[(objective(x),x) for x in seeds];results=[]
    for score,x in choose_diverse(ranked,2):
        y,value=refine_lm(p,x,context,iterations=14)
        results.extend([(score,x),(value,y)])
    score,x=min(results,key=lambda r:r[0])
    after,y=nelder_mead(objective,x,step=.004,iterations=45)
    if after<score:score,x=after,y
    fine=Context(p,count=65,reverse_count=25,
                 geometry=context.geometry)
    choices=[x]+[v for _,v in results]
    final=lambda v:score_norms(sample_norms(unpack(p,v),fine),2)
    score,x=min(((final(x),x) for x in choices),key=lambda r:r[0])
    y,value=refine_lm(p,x,fine,iterations=5)
    if value<score:x=y
    return unpack(p,x),fine

def fit(p,policy='auto',tolerance=.5,control_count=2,metrics=False,check_error=True,decision_only=False,center_limit=0.0,integer_step=0.0,explicit_midpoint=False,cancel=None,tangents=None):
    """Fixed-count policies are internal; auto retains the established one/two fit."""
    if policy not in ('single','auto','pair','probe','multiple'):raise ValueError('Unknown policy')
    values=validated_settings(deviation=tolerance,max_controls=control_count)
    tolerance=values['deviation'];control_count=values['max_controls']
    if len(p)!=4 or any(not math.isfinite(z.real) or not math.isfinite(z.imag) for z in p):
        raise ValueError('Invalid cubic coordinates')
    origin=p[0];scale=max([abs(z-origin) for z in p]+[1e-9])
    normal=tuple((z-origin)/scale for z in p)
    restore=lambda parts:[tuple(origin+scale*z for z in q) for q in parts]
    cache=numeric_cache();source_cache={};context=None;single_error=None
    while len(cache)>64:cache.pop(next(iter(cache)))
    def prepare(parts):
        return adjust_parts([p],parts,tolerance,center_limit,integer_step,explicit_midpoint,
                            context_factory=lambda curves:Context(curves[0]),cancel=cancel,tangents=tangents)
    def result(parts,error,status,norms=None):
        return dict(parts=parts,error=error,within=error[1]<=tolerance if error is not None else None,
                    angles=diagnostics(p,parts),single_error=single_error,status=status,
                    rms=score_norms(norms)*scale if norms is not None else None,tangents=tangents or (None,None))
    if abs(normal[3]-3*normal[2]+3*normal[1]-normal[0])<1e-11:
        one=single_l2(normal)
        count=2 if policy=='pair' else (control_count if policy=='multiple' else 1)
        if count==1:parts=restore([one])
        elif count==2:
            a=(one[0]+one[1])/2;b=(one[1]+one[2])/2;m=(a+b)/2
            parts=restore([(one[0],a,m),(m,b,one[2])])
        else:parts=restore(unpack(normal,subdivision_seed(normal,[i/count for i in range(count+1)])))
        original_parts=parts;parts=prepare(parts)
        error=(geometric_bounds(p,parts,tolerance,reject_above=tolerance if decision_only else None,
                               source_cache=source_cache) if parts!=original_parts else (0.0,scale*1e-10)) if check_error else None
        single_error=error
        return result(parts,error,'EXACT DEGREE REDUCTION')
    if policy not in ('pair','multiple'):
        key=('one',normal)
        if key not in cache:cache[key]=optimize_one(normal,make_context(normal),maximum=False)
        one=cache[key];parts=prepare(restore([one]))
        single_error=geometric_bounds(p,parts,tolerance,
            reject_above=tolerance if decision_only or policy in ('auto','probe') else None,
            source_cache=source_cache) if check_error else None
        if policy in ('single','probe') or not check_error or single_error[1]<=tolerance:
            norms=sample_norms([tuple((z-origin)/scale for z in q) for q in parts],Context(normal)) if metrics else None
            return result(parts,single_error,'ONE QUADRATIC',norms)
    count=control_count if policy=='multiple' else 2
    key=('chain',normal,count)
    if key not in cache:
        geometry=cache.get(('source',normal))
        cache[key],context=optimize_pair(normal,geometry) if count==2 else optimize_chain(normal,count,geometry)
        cache[('source',normal)]=context.geometry
    parts=prepare(restore(cache[key]))
    error=geometric_bounds(p,parts,tolerance,source_cache=source_cache,
                           reject_above=tolerance if decision_only else None) if check_error else None
    norms=sample_norms([tuple((z-origin)/scale for z in q) for q in parts],context or Context(normal)) if metrics else None
    return result(parts,error,'QUADRATIC CHAIN',norms)

def select_simpler(candidates,layers,margin,complete,measure,cancel=None,ceiling=None):
    """Keep the first smaller count within a fixed margin of the current result."""
    def worst(count,results,limit=None):
        upper=0.0
        for i in range(layers):
            if cancel is not None and cancel():raise CancelledError()
            if i==len(results):results.append(complete(i,count))
            r=results[i]
            if r is None:return float('inf')
            error=r['error']
            if limit is not None and error is not None and error[0]>limit:return float('inf')
            error=measure(i,r,limit)
            if limit is not None and error[0]>limit:return float('inf')
            upper=max(upper,error[1])
            if limit is not None and upper>limit:return upper
        return upper
    current=candidates[-1];cost=worst(len(candidates),current)
    threshold=cost+margin
    limit=min(threshold,ceiling) if ceiling is not None else threshold
    for count,results in enumerate(candidates[:-1],1):
        error=worst(count,results,limit)
        if error<threshold and (ceiling is None or error<=ceiling):return results
    if math.isfinite(cost):return current
    raise TangentConflict()

def fit_corresponding(curves,tolerance=.5,max_controls=2,cancel=None,center_limit=0.0,integer_step=0.0,explicit_midpoint=False,center_tolerance=None,tangents=None,comparison_tolerance=None):
    """Find a passing count or the cap, then prefer a simpler fit within the margin."""
    values=validated_settings(deviation=tolerance,max_controls=max_controls)
    tolerance=values['deviation'];max_controls=values['max_controls'];curves=list(curves)
    center_tolerance=tolerance if center_tolerance is None else center_tolerance
    comparison_tolerance=tolerance if comparison_tolerance is None else validated_settings(comparison_tolerance)['deviation']
    options=dict(integer_step=integer_step,explicit_midpoint=explicit_midpoint,cancel=cancel) if integer_step else {}
    if tangents is not None and len(tangents)!=len(curves):raise TangentConflict()
    def check_cancel():
        if cancel is not None and cancel():raise CancelledError()
    def finish(results):
        if any(r is None for r in results):raise TangentConflict()
        if center_limit:
            for i,(p,r) in enumerate(zip(curves,results)):
                parts=center_parts([p],r['parts'],center_tolerance,center_limit,integer_step,
                                   tangents[i] if tangents is not None else None,cancel)
                if parts!=r['parts']:
                    r['parts']=parts;r['angles']=diagnostics(p,parts)
                    r['error']=geometric_bounds(p,parts,center_tolerance);r['within']=r['error'][1]<=center_tolerance
        return results
    def compute(p,count,check_error,index):
        check_cancel();extra=dict(options)
        if tangents is not None:extra['tangents']=tangents[index]
        try:return fit(p,policy='single' if count==1 else ('pair' if count==2 else 'multiple'),
                   tolerance=tolerance,control_count=count,check_error=check_error,decision_only=True,**extra)
        except TangentConflict:return None
    if not curves:return []
    if max_controls==1:return finish([compute(p,1,False,i) for i,p in enumerate(curves)])
    candidates=[]
    for count in range(1,max_controls+1):
        at_limit=count==max_controls;results=[]
        for i,p in enumerate(curves):
            r=compute(p,count,not at_limit,i);results.append(r)
            if not at_limit and (r is None or not r['within']):break
        candidates.append(results)
        if not at_limit and len(results)==len(curves) and all(r is not None and r['within'] for r in results):break
    source_caches=[{} for _ in curves]
    def measure(i,r,limit):
        if r['error'] is None or not r['within']:
            r['error']=geometric_bounds(curves[i],r['parts'],tolerance,
                source_cache=source_caches[i],reject_above=limit)
            r['within']=r['error'][1]<=tolerance
        return r['error']
    return finish(select_simpler(candidates,len(curves),comparison_tolerance/2,
                                lambda i,count:compute(curves[i],count,False,i),measure,cancel))

# -*- coding: utf-8 -*-
"""Fit adjacent cubic pieces jointly, then partition without losing selected data."""
import math
from concurrent.futures import CancelledError

class CompositeContext:
    def __init__(self,curves,count=65,reverse_count=25,geometry=None):
        self.curves=curves;self.p=(curves[0][0],curves[0][1],curves[-1][2],curves[-1][3])
        self.reverse_count=reverse_count
        self.boxes=[(min(z.real for z in p),max(z.real for z in p),min(z.imag for z in p),max(z.imag for z in p)) for p in curves]
        self.box_allowance=max([1.0]+[abs(z) for p in curves for z in p])*1e-12
        if geometry is None:
            contexts=[Context(p,2,reverse_count) for p in curves];line=[];edges=[]
            for i,context in enumerate(contexts):
                line.extend(context.line if not line else context.line[1:])
                edges.extend((i,j) for j in range(len(context.line)-1))
            self.geometry=(contexts,line,edges)
        else:self.geometry=geometry
        self.contexts,self.line,self.edges=self.geometry
        self.prune_source=sum(len(c.line) for c in self.contexts)>32
        lengths=[abs(b-a) for a,b in zip(self.line,self.line[1:])]
        total=sum(lengths);edge=0;before=0.0;self.samples=[]
        for i in range(count):
            target=total*i/(count-1)
            while edge<len(lengths)-1 and before+lengths[edge]<target:before+=lengths[edge];edge+=1
            local=(target-before)/lengths[edge] if lengths[edge] else 0.0
            piece,j=self.edges[edge];context=self.contexts[piece]
            t=context.times[j]+local*(context.times[j+1]-context.times[j])
            weight=(.5 if i in (0,count-1) else 1.0)/(count-1)
            self.samples.append((cubic(curves[piece],t),weight))

    def nearest(self,z):
        if not self.prune_source:
            candidates=[(abs(point-z),i,point,t) for i,c in enumerate(self.contexts) for point,t in [c.nearest(z)]]
            best=min(candidates,key=lambda r:r[:2]);return best[2],(best[1],best[3])
        lower=lambda b:math.hypot(max(b[0]-z.real,0,z.real-b[1]),max(b[2]-z.imag,0,z.imag-b[3]))
        ranked=sorted((lower(box),i) for i,box in enumerate(self.boxes));best=None
        for bound,i in ranked:
            if best is not None and bound-self.box_allowance>best[0]:continue
            point,t=self.contexts[i].nearest(z);candidate=(abs(point-z),i,point,t)
            if best is None or candidate[:2]<best[:2]:best=candidate
        return best[2],(best[1],best[3])

    def tangent(self,t):
        return self.contexts[t[0]].tangent(t[1])

    def interior(self,t):
        return self.contexts[t[0]].interior(t[1])

def composite_seed(context,count):
    matrix=[[0.0]*count for _ in range(count)];rhs=[0j]*count
    for index,(z,weight) in enumerate(context.samples):
        t=index/(len(context.samples)-1);segment=min(count-1,int(t*count));s=t*count-segment;u=1-s
        coefficients=[v.real for v in basis(s,segment,count)[::2]]
        target=z
        if segment==0:target-=u*u*context.p[0]
        if segment==count-1:target-=s*s*context.p[3]
        active=[(i,v) for i,v in enumerate(coefficients) if v]
        for i,a in active:
            rhs[i]+=weight*a*target
            for j,b in active:matrix[i][j]+=weight*a*b
    real=solve(matrix,[z.real for z in rhs]);imag=solve(matrix,[z.imag for z in rhs])
    return [v for a,b in zip(real,imag) for v in (a,b)]

def optimize_composite(curves,count,geometry=None):
    if count==1:
        proxy=(curves[0][0],curves[0][1],curves[-1][2],curves[-1][3]);exact=intersection(proxy)
        allowance=max([1.0]+[abs(z) for p in curves for z in p])*1.01e-10
        if exact is not None and single_quadratic_bound(curves,exact)<=allowance:return [exact],geometry
    context=CompositeContext(curves,max(65,16*len(curves)+1,12*count+1),17,geometry)
    p=context.p;seeds=[subdivision_seed(p,[i/count for i in range(count+1)])]
    try:seeds.append(composite_seed(context,count))
    except ValueError:pass
    if count==len(curves):seeds.append(pack([single_l2(p) for p in curves]))
    objective=lambda x:score_norms(sample_norms(unpack(p,x),context))
    candidates=sorted(((objective(x),x) for x in seeds),key=lambda r:r[0])
    for _,x in candidates[:2]:
        y,value=refine_lm(p,x,context,iterations=14);candidates.append((value,y))
    score,x=min(candidates,key=lambda r:r[0])
    if count==1:
        after,y=nelder_mead(objective,x,step=.004,iterations=100)
        if after<score:x=y
    fine=CompositeContext(curves,max(97,20*len(curves)+1,16*count+1),25,context.geometry)
    final=lambda x:score_norms(sample_norms(unpack(p,x),fine))
    score,x=min(((final(v),v) for v in [x]+[y for _,y in candidates]),key=lambda r:r[0])
    y,value=refine_lm(p,x,fine,iterations=5)
    if value<score:x=y
    return unpack(p,x),fine.geometry

def single_quadratic_bound(curves,q):
    """A monotone parameter correspondence gives a conservative control-hull bound."""
    times=[0.0]+[nearest_quadratic(p[3],q)[1] for p in curves[:-1]]+[1.0]
    if any(b<a for a,b in zip(times,times[1:])):return float('inf')
    upper=0.0
    for p,a,b in zip(curves,times,times[1:]):
        start=quadratic(q,a);end=quadratic(q,b)
        control=start+(b-a)*((1-a)*(q[1]-q[0])+a*(q[2]-q[1]))
        elevated=(start,(start+2*control)/3,(2*control+end)/3,end)
        upper=max(upper,max(abs(x-y) for x,y in zip(p,elevated)))
    return upper+max([1.0]+[abs(z) for p in curves for z in p]+list(map(abs,q)))*1e-10

def fit_merged_count(curves,count,tolerance,geometries,bounds_cache,center_limit=0.0,integer_step=0.0,explicit_midpoint=False,cancel=None,tangents=None,center_tolerance=None):
    origin=curves[0][0];scale=max([abs(z-origin) for p in curves for z in p]+[1e-9])
    normal=tuple(tuple((z-origin)/scale for z in p) for p in curves)
    cache=numeric_cache();key=('merged',normal,count)
    if key not in cache:
        cache[key],geometries[normal]=optimize_composite(normal,count,geometries.get(normal))
        while len(cache)>64:cache.pop(next(iter(cache)))
    parts=[tuple(origin+scale*z for z in q) for q in cache[key]]
    parts=adjust_parts(curves,parts,tolerance,0.0,integer_step,explicit_midpoint,
                       context_factory=CompositeContext,cancel=cancel,tangents=tangents)
    if center_limit:
        parts=center_parts(curves,parts,tolerance if center_tolerance is None else center_tolerance,
                           center_limit,integer_step,tangents,cancel)
    proxy=(curves[0][0],curves[0][1],curves[-1][2],curves[-1][3])
    bound=single_quadratic_bound(curves,parts[0]) if count==1 else float('inf')
    error=(0.0,bound) if bound<=tolerance else geometric_bounds(
        proxy,parts,tolerance,accuracy=min(max(.002,tolerance*.02),tolerance*.1),
        reject_above=tolerance,source_cache=bounds_cache,source_curves=curves)
    return dict(parts=parts,error=error,within=error[1]<=tolerance,angles=diagnostics(proxy,parts),tangents=tangents or (None,None))

def try_merged_corresponding(chains,tolerance,max_controls,cancel=None,tangents=None,**options):
    geometries={};bounds_cache={};candidates=[]
    def compute(i,count):
        if cancel is not None and cancel():raise CancelledError()
        extra=dict(options)
        if tangents is not None:extra['tangents']=tangents[i]
        try:return fit_merged_count(chains[i],count,tolerance,geometries,bounds_cache,cancel=cancel,**extra)
        except TangentConflict:return None
    def measure(i,r,limit):
        if r['error'] is None or not r['within']:
            curves=chains[i];proxy=(curves[0][0],curves[0][1],curves[-1][2],curves[-1][3])
            r['error']=geometric_bounds(proxy,r['parts'],tolerance,
                accuracy=min(max(.002,tolerance*.02),tolerance*.1),reject_above=limit,
                source_cache=bounds_cache,source_curves=curves)
            r['within']=r['error'][1]<=tolerance
        return r['error']
    for count in range(1,max_controls+1):
        results=[]
        for i in range(len(chains)):
            r=compute(i,count);results.append(r)
            if r is None or not r['within']:break
        candidates.append(results)
        if len(results)==len(chains) and all(r is not None and r['within'] for r in results):
            return select_simpler(candidates,len(chains),tolerance/2,compute,measure,cancel,ceiling=tolerance)
    return None

def fit_run_corresponding(chains,tolerance=.5,max_controls=2,cyclic=False,cancel=None,center_limit=0.0,integer_step=0.0,explicit_midpoint=False,single_tolerance=None,angle_limit=2.0,tangents=None,center_tolerance=None,join_tangents=None):
    """Whole first; failed runs choose a complete, non-overlapping partition."""
    settings=validated_settings(tolerance,max_controls,angle_limit=angle_limit);tolerance=settings['deviation'];max_controls=settings['max_controls'];angle_limit=settings['angle_limit']
    chains=tuple(tuple(map(tuple,chain)) for chain in chains)
    if not chains:raise ValueError('Invalid corresponding curve runs')
    length=len(chains[0])
    if any(len(chain)!=length for chain in chains) or not length:raise ValueError('Invalid corresponding curve runs')
    if any(len(p)!=4 or any(not math.isfinite(z.real) or not math.isfinite(z.imag) for z in p) for chain in chains for p in chain):raise ValueError('Invalid cubic coordinates')
    if any(a[3]!=b[0] for chain in chains for a,b in zip(chain,chain[1:])):raise ValueError('Non-contiguous cubic run')
    if cyclic and any(chain[-1][3]!=chain[0][0] for chain in chains):raise ValueError('Non-closed cubic run')
    options=dict(center_limit=center_limit,integer_step=integer_step,explicit_midpoint=explicit_midpoint) if center_limit or integer_step else {}
    single_tolerance=tolerance if single_tolerance is None else single_tolerance
    center_tolerance=tolerance if center_tolerance is None else center_tolerance
    candidates={}
    def candidate(start,count):
        if cancel is not None and cancel():raise CancelledError()
        key=(start%length,count)
        if key not in candidates:
            boundary_tangents=[(pair[0] if start%length==0 else None,pair[1] if (start+count)%length==0 else None) for pair in tangents] if tangents is not None else None
            if join_tangents is not None:
                boundary_tangents=[(pairs[start%length][0],pairs[(start+count-1)%length][1]) for pairs in join_tangents]
            extra=dict(options)
            if boundary_tangents is not None:extra['tangents']=boundary_tangents
            if count==1:
                candidates[key]=fit_corresponding([chain[start%length] for chain in chains],single_tolerance,max_controls,cancel,center_tolerance=center_tolerance,comparison_tolerance=tolerance,**extra)
            else:
                subset=[tuple(chain[(start+i)%length] for i in range(count)) for chain in chains]
                smooth=all(smooth_join(a,b,angle_limit) for chain in subset for a,b in zip(chain,chain[1:]))
                candidates[key]=try_merged_corresponding(subset,tolerance,max_controls,cancel,center_tolerance=center_tolerance,**extra) if smooth else None
        return candidates[key]
    if length==1:return [dict(start=0,count=1,fits=candidate(0,1))]
    whole=candidate(0,length)
    if whole is not None:return [dict(start=0,count=length,fits=whole)]
    def partition(rotation):
        best=[None]*(length+1);best[length]=((0,0.0,0),[])
        for offset in range(length-1,-1,-1):
            choices=[]
            for count in range(length-offset,0,-1):
                fits=candidate(rotation+offset,count)
                if fits is None:continue
                tail,blocks=best[offset+count]
                error=max(r['error'][1] for r in fits) if count>1 else 0.0
                cost=(tail[0]+1,max(error,tail[1]),tail[2]+len(fits[0]['parts']))
                block=dict(start=(rotation+offset)%length,count=count,fits=fits)
                choices.append((cost,[block]+blocks))
            best[offset]=min(choices,key=lambda r:r[0])
        return best[0]
    return min((partition(i) for i in range(length if cyclic else 1)),key=lambda r:r[0])[1]


def native_preflight(GSNode, GSPath, make_point, constants, add_midpoint=False, max_controls=2):
    """Exercise actual NSPoint, node and native quadratic drawing APIs."""
    offcurve, curve, qcurve = constants
    probe = GSPath()
    probe.closed = False
    nodes = []
    for xy, kind in [((0,0), 'line'), ((40,80), offcurve), ((100,0), qcurve)]:
        node = GSNode()
        node.position = make_point(float(xy[0]), float(xy[1]))
        node.type = kind
        nodes.append(node)
    probe.nodes = nodes
    actual = list(probe.nodes)
    if len(actual) != 3 or actual[-1].type != qcurve:
        raise RuntimeError(tr('native'))
    # NSBezierPath.bounds is tight geometric bounds, not controlPointBounds.
    rect = probe.bezierPath.bounds()
    values = (rect.origin.x, rect.origin.y, rect.size.width, rect.size.height)
    if max(abs(float(a)-b) for a,b in zip(values,(0.0,0.0,100.0,40.0))) > 1e-5:
        raise RuntimeError(tr('native')+' ' + repr(values))
    implicit = GSPath()
    implicit.closed = False
    nodes = []
    for xy, kind in [((0,0),'line'), ((0,100),offcurve),
                     ((100,100),offcurve), ((100,0),qcurve)]:
        node = GSNode()
        node.position = make_point(float(xy[0]),float(xy[1]))
        node.type = kind
        nodes.append(node)
    implicit.nodes = nodes
    if len(implicit.nodes) != 4 or sum(n.type != offcurve for n in implicit.nodes) != 2:
        raise RuntimeError(tr('native'))
    rect = implicit.bezierPath.bounds()
    values = (rect.origin.x,rect.origin.y,rect.size.width,rect.size.height)
    if max(abs(float(a)-b) for a,b in zip(values,(0,0,100,100))) > 1e-5:
        raise RuntimeError(tr('native')+' ' + repr(values))



    if add_midpoint:
        explicit=GSPath();explicit.closed=False;nodes=[]
        for xy,kind in [((0,0),'line'),((0,100),offcurve),((50,100),qcurve),
                        ((100,100),offcurve),((100,0),qcurve)]:
            node=GSNode();node.position=make_point(float(xy[0]),float(xy[1]))
            node.type=kind;nodes.append(node)
        nodes[2].smooth=True;explicit.nodes=nodes
        rect=explicit.bezierPath.bounds()
        values=(rect.origin.x,rect.origin.y,rect.size.width,rect.size.height)
        if len(explicit.nodes)!=5 or max(abs(float(a)-b) for a,b in zip(values,(0,0,100,100)))>1e-5:
            raise RuntimeError(tr('native')+' '+repr(values))

    if max_controls>2:
        count=3
        chain=GSPath();chain.closed=False;nodes=[]
        points=[(0.0,'line')]+[(100.0*(i+.5)/count,offcurve) for i in range(count)]+[(100.0,qcurve)]
        for x,kind in points:
            node=GSNode();node.position=make_point(x,0.0);node.type=kind;nodes.append(node)
        chain.nodes=nodes;rect=chain.bezierPath.bounds()
        values=(rect.origin.x,rect.origin.y,rect.size.width,rect.size.height)
        if len(chain.nodes)!=count+2 or max(abs(float(a)-b) for a,b in zip(values,(0,0,100,0)))>1e-5:
            raise RuntimeError(tr('native')+' '+repr(values))

# -*- coding: utf-8 -*-
"""Selection, synchronized masters, staged edits and one undo transaction."""
import math
from contextlib import ExitStack
from collections import deque
from builtins import id as _python_id
try:
    from objc import pyobjc_id as _objc_id
except ImportError:
    _objc_id=None


def object_id(obj):
    """Native pointers survive recreation of Python proxy wrappers."""
    if _objc_id is not None and obj is not None:
        try:return _objc_id(obj)
        except (TypeError,ValueError):pass
    return _python_id(obj)


class ConversionError(RuntimeError):
    pass


def flag(obj,name,default=False):
    value=getattr(obj,name,default)
    return value() if callable(value) else value


def validate_nodes(nodes,closed,offcurve,curve,qcurve,overrides=None):
    overrides=overrides or {};types=[overrides.get(i,n.type) for i,n in enumerate(nodes)]
    ons=[i for i,t in enumerate(types) if t!=offcurve]
    if not ons:return bool(closed) and bool(nodes)
    if not closed and (ons[0]!=0 or ons[-1]!=len(nodes)-1):return False
    pairs=list(zip(ons,ons[1:]))
    if closed:pairs.append((ons[-1],ons[0]+len(nodes)))
    for start,end in pairs:
        count=end-start-1;kind=types[end%len(nodes)]
        if kind==curve:
            if count!=2:return False
        elif kind==qcurve:
            if count<1:return False
        elif count:return False
    return True


def cubic_keys(layer,constants,selected=False):
    offcurve,curve,qcurve=constants;keys=set()
    for pi,path in enumerate(layer.paths):
        nodes=list(path.nodes);n=len(nodes)
        if n<3:continue
        for i in range(n if path.closed else max(0,n-3)):
            part=[nodes[(i+j)%n] for j in range(4)]
            if not (part[0].type!=offcurve and part[1].type==offcurve and
                    part[2].type==offcurve and part[3].type==curve):continue
            if not selected or ((part[0].selected and part[3].selected) or
                                (part[1].selected and part[2].selected)):
                keys.add((pi,i))
    return keys


def layer_for_master(glyph,master_id):
    try:layer=glyph.layers[master_id]
    except (KeyError,TypeError,IndexError):layer=None
    if layer is None:raise ConversionError(tr('missing_master')+str(master_id))
    return layer


def structure(layer):
    shapes=[]
    for shape in layer.shapes:
        if hasattr(shape,'nodes'):
            shapes.append(('path',bool(shape.closed),tuple(n.type for n in shape.nodes),
                           flag(shape,'direction',None)))
        else:shapes.append(('component',str(shape.componentName)))
    anchors=tuple(sorted(a if isinstance(a,str) else str(a.name) for a in layer.anchors))
    return str(layer.compareString()),tuple(shapes),anchors


def layer_glyph(layer):
    parent=getattr(layer,'parent',None)
    if parent is not None and hasattr(parent,'layers'):return parent
    foreground=flag(layer,'foreground',None)
    return getattr(foreground,'parent',None) if foreground is not None else None


def independent_layer(layer):
    return flag(layer,'foreground',None) is not None or not (flag(layer,'isMasterLayer') or flag(layer,'isSpecialLayer'))


def synchronized_layers(font,glyph,sources,constants,independent=False):
    if independent:
        layers=list(sources)
        for layer in layers:
            foreground=flag(layer,'foreground',None)
            attached=(object_id(flag(foreground,'background',None))==object_id(layer) and object_id(layer_glyph(foreground))==object_id(glyph)) if foreground is not None else any(object_id(layer)==object_id(x) for x in glyph.layers)
            if not attached:raise ConversionError(tr('changed_layers'))
    else:
        layers=[layer_for_master(glyph,m.id) for m in font.masters]
        for layer in glyph.layers:
            if flag(layer,'isSpecialLayer') and all(object_id(layer)!=object_id(x) for x in layers):layers.append(layer)
    if not layers:raise ConversionError(tr('no_master'))
    if any(all(object_id(source)!=object_id(x) for x in layers) for source in sources):
        raise ConversionError(tr('changed_layers'))
    if not independent and len(layers)>1 and not bool(glyph.mastersCompatible):
        raise ConversionError(tr('incompatible'))
    expected=structure(layers[0])
    for layer in layers:
        if structure(layer)!=expected:
            raise ConversionError(tr('structure'))
        if any(not validate_nodes(list(p.nodes),bool(p.closed),*constants) for p in layer.paths):
            raise ConversionError(tr('unsupported'))
    return layers


def selected_requests(font,constants):
    requests=[]
    if font.currentTab is None:
        # Font View selection is separate from the Edit View layer selection.
        for glyph in list(font.selection or []):
            requests.append((glyph,layer_for_master(glyph,font.selectedFontMaster.id),True,set()))
    else:
        layers=list(font.selectedLayers or [])
        active=flag(font.currentTab,'activeLayer',None)
        if active is None:
            try:active=flag(font.parent.windowController(),'activeLayer',None)
            except AttributeError:pass
        foreground=flag(active,'foreground',None) if active is not None else None
        if foreground is not None and layers:
            layers=[active if object_id(layer)==object_id(foreground) else layer for layer in layers]
        if not layers:
            # A text insertion cursor can have an active glyph without a range.
            if active is None:
                tab=font.currentTab;visible=list(getattr(tab,'layers',[]) or [])
                cursor=int(getattr(tab,'layersCursor',0))
                active=visible[cursor] if 0<=cursor<len(visible) else None
            if active is not None:layers=[active]
        for layer in layers:
            glyph=layer_glyph(layer)
            if glyph is None or not hasattr(glyph,'layers'):continue
            whole=not bool(list(layer.selection))
            requests.append((glyph,layer,whole,cubic_keys(layer,constants,selected=True)))
    return requests


def prepare_tasks(font,constants):
    initial=selected_requests(font,constants)
    if not initial:return [],[],[]
    registry={};queue=deque()
    def add(glyph,layer,whole,keys):
        independent=independent_layer(layer);name=(glyph.name,object_id(layer) if independent else None)
        if name not in registry:
            registry[name]=dict(glyph=glyph,sources=[],whole=False,keys=set(),revision=0,independent=independent)
        item=registry[name]
        changed=(whole and not item['whole']) or not keys.issubset(item['keys'])
        if all(object_id(layer)!=object_id(x) for x in item['sources']):item['sources'].append(layer);changed=True
        item['whole']|=whole;item['keys'].update(keys)
        if changed:item['revision']+=1;queue.append((name,item['revision']))
    for args in initial:add(*args)
    checked={};invalid=set()
    while queue:
        name,revision=queue.popleft();item=registry[name]
        if revision!=item['revision'] or name in invalid:continue
        try:layers=synchronized_layers(font,item['glyph'],item['sources'],constants,item['independent'])
        except Exception:invalid.add(name);continue
        checked[name]=layers
        # Components remain references. Convert their base glyphs recursively.
        names=set()
        for source in ([] if item['independent'] else item['sources']):
            for comp in source.components:
                if item['whole'] or bool(flag(comp,'selected')):names.add(str(comp.componentName))
        for base_name in sorted(names):
            try:
                base=font.glyphs[base_name]
                if base is None:raise KeyError(base_name)
                add(base,layer_for_master(base,font.selectedFontMaster.id),True,set())
            except Exception:invalid.add(name)
    tasks=[];groups=[];guards=[]
    for name,item in registry.items():
        if name in invalid:continue
        layers=checked[name]
        item['layers']=layers
        item['snapshots']={object_id(l):[(p,tuple(p.nodes),path_state(p)) for p in l.paths] for l in layers}
        item['structure_before']={object_id(l):structure(l) for l in layers}
        guards.append(item)
        keys=cubic_keys(layers[0],constants) if item['whole'] else item['keys']
        if not keys:continue
        # Native hints can reference off-curve nodes. Do not leave dangling refs.
        removed=set()
        for layer in layers:
            for pi,i in keys:
                nodes=list(layer.paths[pi].nodes);n=len(nodes)
                removed.update(object_id(nodes[(i+j)%n]) for j in (1,2))
        hints_bad=any(object_id(getattr(h,key,None)) in removed for l in layers for h in l.hints
                      for key in ('originNode','targetNode','otherNode1','otherNode2'))
        if hints_bad:continue
        item['keys']=keys
        item['selected_sources']={object_id(l) for l in item['sources']} if not item['whole'] else set()
        tasks.append(item)
        groups.extend((item,pi,i) for pi,i in sorted(keys))
    return tasks,groups,guards


def curve_runs(tasks,angle_limit=2.0):
    """Only selected cubics are grouped; native hint targets remain boundaries."""
    groups=[]
    for item in tasks:
        by_path={}
        for pi,i in item['keys']:by_path.setdefault(pi,set()).add(i)
        for pi,starts in sorted(by_path.items()):
            path=item['layers'][0].paths[pi];n=len(path.nodes);closed=bool(path.closed);protected=set()
            for layer in item['layers']:
                references={object_id(getattr(h,key)) for h in layer.hints
                            for key in ('originNode','targetNode','otherNode1','otherNode2')
                            if getattr(h,key,None) is not None}
                protected.update(i for i in starts if object_id(layer.paths[pi].nodes[i]) in references)
            for i in starts:
                previous=(i-3)%n if closed else i-3
                if previous not in starts:continue
                for layer in item['layers']:
                    nodes=layer.paths[pi].nodes
                    point=lambda j:complex(float(nodes[j%n].position.x),float(nodes[j%n].position.y))
                    if not aligned(point(i)-point(i-1),point(i+1)-point(i),angle_limit):protected.add(i);break
            def successor(i):
                next_i=(i+3)%n if closed else i+3
                return next_i if next_i in starts and next_i not in protected else None
            def has_previous(i):
                previous=(i-3)%n if closed else i-3
                return i not in protected and previous in starts
            visited=set()
            for start in sorted(i for i in starts if not has_previous(i))+sorted(starts):
                if start in visited:continue
                indices=[];i=start
                while i is not None and i not in visited:
                    visited.add(i);indices.append(i);i=successor(i)
                groups.append((item,pi,indices,closed and i==start))
    return groups


def line_tangents(layer,pi,indices,constants,angle_limit):
    path=layer.paths[pi];nodes=path.nodes;n=len(nodes);closed=bool(path.closed)
    offcurve,curve,qcurve=constants;start=indices[0];end=(indices[-1]+3)%n
    point=lambda i:complex(float(nodes[i%n].position.x),float(nodes[i%n].position.y))
    left=right=None
    if (closed or start>0) and nodes[(start-1)%n].type!=offcurve and nodes[start].type not in constants:
        direction=point(start)-point(start-1)
        if aligned(point(start+1)-point(start),direction,angle_limit/2):left=(point(start),direction)
    if (closed or end<n-1) and nodes[(end+1)%n].type not in constants:
        direction=point(end)-point(end+1)
        if aligned(point(end-1)-point(end),direction,angle_limit/2):right=(point(end),direction)
    return left,right


def curve_tangents(layer,pi,indices,constants,angle_limit):
    path=layer.paths[pi];nodes=path.nodes;n=len(nodes);closed=bool(path.closed)
    offcurve,curve,qcurve=constants
    point=lambda i:complex(float(nodes[i%n].position.x),float(nodes[i%n].position.y))
    def at_join(i):
        if not closed and (i<3 or i+3>=n):return None
        if not (nodes[i%n].type==curve and nodes[(i-1)%n].type==offcurve and
                nodes[(i-2)%n].type==offcurve and nodes[(i-3)%n].type!=offcurve and
                nodes[(i+1)%n].type==offcurve and nodes[(i+2)%n].type==offcurve and
                nodes[(i+3)%n].type==curve):return None
        incoming=point(i)-point(i-1);outgoing=point(i+1)-point(i)
        if not aligned(incoming,outgoing,angle_limit):return None
        mean=incoming/abs(incoming)+outgoing/abs(outgoing)
        return mean/abs(mean) if abs(mean)>1e-12 else None
    start=indices[0];end=(indices[-1]+3)%n;left=at_join(start);right=at_join(end)
    return ((point(start),left) if left is not None else None,
            (point(end),-right) if right is not None else None)


def path_state(path):
    return bool(path.closed),tuple((object_id(n),n.type,float(n.position.x),float(n.position.y),bool(n.smooth))
                                   for n in path.nodes)


def build_path_plan(path,results,GSNode,make_point,constants,sharp,add_midpoint=False):
    offcurve,curve,qcurve=constants;nodes=list(path.nodes);n=len(nodes)
    edits={};types={};new=[]
    for i,result in sorted(results.items()):
        span=result.get('source_count',1)
        ids=[(i+j)%n for j in range(3*span+1)];controls=[]
        for part_index,q in enumerate(result['parts']):
            node=GSNode();node.position=make_point(float(q[1].real),float(q[1].imag));node.type=offcurve
            controls.append(node);new.append(node)
            if add_midpoint and part_index<len(result['parts'])-1:
                m=q[2] if result.get('integer_coords') else (q[1]+result['parts'][part_index+1][1])/2
                midpoint=GSNode();midpoint.position=make_point(float(m.real),float(m.imag))
                midpoint.type=qcurve;midpoint.smooth=True
                controls.append(midpoint);new.append(midpoint)
        edits[ids[1]]=controls
        for index in ids[2:-1]:edits[index]=[]
        types[ids[-1]]=qcurve
    output=[];mapping={}
    for i,node in enumerate(nodes):
        if i in edits:output.extend(edits[i])
        else:mapping[i]=len(output);output.append(node)
    if not validate_nodes(output,bool(path.closed),*constants,
                          overrides={mapping[i]:kind for i,kind in types.items()}):
        raise ConversionError(tr('invalid_nodes'))
    return dict(path=path,original=nodes,output=output,
                types=[(nodes[i],kind) for i,kind in types.items()],
                sharp=[nodes[i] for i in sharp],new=new,
                removed={object_id(nodes[i]) for i in edits},
                status=[(node,node.type,bool(node.smooth)) for node in nodes])


def commit_plans(font,batches,tasks,constants):
    # Recheck structure and coordinates after asynchronous planning, before writes.
    for item in tasks:
        if object_id(item['glyph'].parent)!=object_id(font):raise ConversionError(tr('left_font'))
        for layer in item['layers']:
            if structure(layer)!=item['structure_before'][object_id(layer)]:
                raise ConversionError(tr('changed_structure')+item['glyph'].name)
            original=item['snapshots'][object_id(layer)];current=list(layer.paths)
            if len(current)!=len(original) or any(object_id(p)!=object_id(old) or path_state(p)!=state
                   for p,(old,retained_nodes,state) in zip(current,original)):
                raise ConversionError(tr('edited')+item['glyph'].name)
        current_layers=synchronized_layers(font,item['glyph'],item['sources'],constants,item['independent'])
        if [object_id(l) for l in current_layers]!=[object_id(l) for l in item['layers']]:
            raise ConversionError(tr('changed_layers'))
    for layer,plans,select_new in batches:
        removed={key for plan in plans for key in plan['removed']}
        if any(object_id(getattr(h,key,None)) in removed for h in layer.hints
               for key in ('originNode','targetNode','otherNode1','otherNode2')):
            raise ConversionError(tr('hint_changed'))
    old_selection={object_id(layer):list(layer.selection) for layer,plans,select_new in batches}
    document=getattr(font,'parent',None)
    manager=document.undoManager() if document is not None else None
    with ExitStack() as stack:
        font.disableUpdateInterface();stack.callback(font.enableUpdateInterface)
        if manager is not None:
            manager.beginUndoGrouping();stack.callback(manager.endUndoGrouping)
        for layer,plans,select_new in batches:
            layer.beginChanges();stack.callback(layer.endChanges)
        try:
            for layer,plans,select_new in batches:
                removed={key for plan in plans for key in plan['removed']}
                selection=[x for x in old_selection[object_id(layer)] if object_id(x) not in removed]
                for plan in plans:
                    for node,kind in plan['types']:node.type=kind
                    for node in plan['sharp']:node.smooth=False
                    plan['path'].nodes=plan['output']
                    if select_new:selection.extend(plan['new'])
                layer.selection=selection
            for item in tasks:
                if not item['independent'] and len(item['layers'])>1 and not bool(item['glyph'].mastersCompatible):
                    raise ConversionError(tr('post_compat')+item['glyph'].name)
        except Exception as original:
            failures=[]
            for layer,plans,select_new in reversed(batches):
                for plan in reversed(plans):
                    try:
                        for node,kind,smooth in plan['status']:node.type=kind;node.smooth=smooth
                        plan['path'].nodes=plan['original']
                    except Exception as exc:failures.append(str(exc))
                try:layer.selection=old_selection[object_id(layer)]
                except Exception as exc:failures.append(str(exc))
            if failures:raise ConversionError(str(original)+tr('rollback')+'；'.join(failures)) from original
            raise


def conversion_steps(font,GSNode,make_point,constants,tolerance=1.0,max_controls=2,
                     active_font=None,add_midpoint=False,preflight=None,fit_runner=None,merge_curves=False,center_limit=0.0,integer_coords=False,angle_limit=2.0,keep_line_tangent=False,keep_curve_tangent=False):
    values=validated_settings(tolerance,max_controls,add_midpoint,merge_curves=merge_curves,center_limit=center_limit,integer_coords=integer_coords,angle_limit=angle_limit,keep_line_tangent=keep_line_tangent,keep_curve_tangent=keep_curve_tangent)
    tolerance=values['deviation'];max_controls=values['max_controls'];add_midpoint=values['add_midpoint'];merge_curves=values['merge_curves']
    upm=float(getattr(font,'upm',1000));font_scale=upm/1000
    if not math.isfinite(upm) or upm<=0:raise ConversionError(tr('invalid_upm'))
    tolerance*=font_scale
    options=dict(center_limit=values['center_limit']*font_scale,integer_step=1.0 if values['integer_coords'] else 0.0,
                 explicit_midpoint=add_midpoint) if values['center_limit'] or values['integer_coords'] else {}
    tasks,groups,guards=prepare_tasks(font,constants)
    groups=curve_runs(tasks,values['angle_limit']) if merge_curves else [(item,pi,[i],False) for item,pi,i in groups]
    total=len(groups);results={};sharp={}
    if not groups:return False
    if preflight is not None:preflight()
    yield dict(done=0,total=total,glyph=tr('preparing'))
    for done,(item,pi,indices,cyclic) in enumerate(groups,1):
        if active_font is not None and object_id(active_font())!=object_id(font):raise ConversionError(tr('changed_font'))
        chains=[]
        for layer in item['layers']:
            nodes=list(layer.paths[pi].nodes);n=len(nodes)
            chains.append(tuple(tuple(complex(float(nodes[(i+j)%n].position.x),float(nodes[(i+j)%n].position.y))
                                      for j in range(4)) for i in indices))
        progress=dict(done=done-1,total=total,glyph=item['glyph'].name)
        extra=dict(options,center_tolerance=tolerance/2)
        if values['keep_line_tangent'] or values['keep_curve_tangent']:
            joins=[]
            for layer in item['layers']:
                pairs=[]
                for i in indices:
                    line=line_tangents(layer,pi,[i],constants,values['angle_limit']) if values['keep_line_tangent'] else (None,None)
                    curve=curve_tangents(layer,pi,[i],constants,values['angle_limit']) if values['keep_curve_tangent'] else (None,None)
                    pairs.append(tuple(a if a is not None else b for a,b in zip(line,curve)))
                joins.append(pairs)
            if len(indices)>1:extra['join_tangents']=joins
            else:extra['tangents']=[pairs[0] for pairs in joins]
        if len(indices)>1:
            if fit_runner is None:blocks=fit_run_corresponding(chains,tolerance,max_controls,cyclic,single_tolerance=tolerance/2,angle_limit=values['angle_limit'],**extra)
            else:blocks=yield from fit_runner(chains,tolerance,max_controls,progress,merge=True,cyclic=cyclic,single_tolerance=tolerance/2,angle_limit=values['angle_limit'],**extra)
        else:
            curves=[chain[0] for chain in chains]
            if fit_runner is None:fits=fit_corresponding(curves,tolerance/2,max_controls,comparison_tolerance=tolerance,**extra)
            else:fits=yield from fit_runner(curves,tolerance/2,max_controls,progress,comparison_tolerance=tolerance,**extra)
            blocks=[dict(start=0,count=1,fits=fits)]
        for block in blocks:
            i=indices[block['start']];span=block['count'];fits=block['fits']
            if len({len(r['parts']) for r in fits})!=1:raise ConversionError(tr('count_mismatch'))
            any_angle=[any(r['angles'][k] is not None and abs(r['angles'][k])>1e-6 and not r.get('tangents',(None,None))[k] for r in fits) for k in (0,1)]
            for layer,r in zip(item['layers'],fits):
                key=(object_id(layer),pi);result=dict(r,source_count=span,integer_coords=values['integer_coords'])
                results.setdefault(key,{})[i]=result
                n=len(layer.paths[pi].nodes)
                sharp.setdefault(key,set()).update((i+(0 if k==0 else 3*span))%n for k in (0,1) if any_angle[k])
        yield dict(done=done,total=total,glyph=item['glyph'].name)
    batches=[]
    for item in tasks:
        for layer in item['layers']:
            plans=[]
            for pi,path in enumerate(layer.paths):
                key=(object_id(layer),pi)
                if key in results:plans.append(build_path_plan(path,results[key],GSNode,make_point,constants,sharp[key],add_midpoint=add_midpoint))
            if plans:batches.append((layer,plans,object_id(layer) in item['selected_sources']))
    if active_font is not None and object_id(active_font())!=object_id(font):raise ConversionError(tr('changed_font'))
    if float(getattr(font,'upm',1000))!=upm:raise ConversionError(tr('changed_upm'))
    if batches:commit_plans(font,batches,guards,constants)
    return bool(batches)


def make_job(tolerance=1.0,max_controls=3,add_midpoint=False,fit_runner=None,merge_curves=True,center_limit=7.0,integer_coords=True,angle_limit=5.0,keep_line_tangent=True,keep_curve_tangent=True):
    from GlyphsApp import Glyphs,GSNode,GSPath,OFFCURVE,CURVE,QCURVE
    from Foundation import NSMakePoint
    values=validated_settings(tolerance,max_controls,add_midpoint,merge_curves=merge_curves,center_limit=center_limit,integer_coords=integer_coords,angle_limit=angle_limit,keep_line_tangent=keep_line_tangent,keep_curve_tangent=keep_curve_tangent)
    tolerance=values['deviation'];max_controls=values['max_controls'];add_midpoint=values['add_midpoint'];merge_curves=values['merge_curves']
    font=Glyphs.font
    if font is None:raise ConversionError(tr('no_font'))
    constants=(OFFCURVE,CURVE,QCURVE)
    preflight=lambda:native_preflight(GSNode,GSPath,NSMakePoint,constants,add_midpoint=add_midpoint,max_controls=max_controls)
    return conversion_steps(font,GSNode,NSMakePoint,constants,tolerance,max_controls,
                            lambda:Glyphs.font,add_midpoint,preflight,fit_runner,merge_curves,center_limit,integer_coords,angle_limit,keep_line_tangent,keep_curve_tangent)


def show_message(text,title=None):
    from GlyphsApp import Message
    Message(title=title or tr('title'),message=text,OKButton=tr('ok'))

def glyphs_main(tolerance=1.0,max_controls=3,add_midpoint=False,merge_curves=True,center_limit=7.0,integer_coords=True,angle_limit=3.0,keep_line_tangent=True,keep_curve_tangent=True):
    from GlyphsApp import Glyphs
    job=make_job(tolerance,max_controls,add_midpoint,merge_curves=merge_curves,center_limit=center_limit,integer_coords=integer_coords,angle_limit=angle_limit,keep_line_tangent=keep_line_tangent,keep_curve_tangent=keep_curve_tangent)
    while True:
        try:next(job)
        except StopIteration as done:
            if done.value:Glyphs.redraw()
            return done.value
