// Servidor de registro para el evento: un solo .exe, sin instalar nada.
// La tableta (y otros dispositivos) se conectan por WiFi a esta computadora.
package main

import (
	_ "embed"
	"encoding/base64"
	"encoding/json"
	"fmt"
	"net"
	"net/http"
	"os"
	"os/exec"
	"path/filepath"
	"regexp"
	"runtime"
	"sort"
	"strconv"
	"strings"
	"sync"
	"time"
)

//go:embed registro-evento.html
var pagina []byte

const puerto = 8000

type Registro struct {
	Folio    int    `json:"folio"`
	Nombre   string `json:"nombre"`
	Telefono string `json:"telefono"`
	Fecha    string `json:"fecha"`
	Firma    bool   `json:"firma"`
	UID      string `json:"uid,omitempty"`
	Disp     string `json:"disp,omitempty"`
	Rep      string `json:"representante,omitempty"`
}

// Dispositivo que se conecta para registrar (tableta, celular, computadora).
type Dispositivo struct {
	ID     string    `json:"id"`
	Nombre string    `json:"nombre"`
	Ultima time.Time `json:"-"`
}

var (
	mu        sync.Mutex
	registros []Registro
	uids      = map[string]int{}
	disps     = map[string]*Dispositivo{}
	cuenta    = map[string]int{}
	version   = time.Now().Unix()
	dirDatos  string
	dirImg    string
	archivoDB string
	soloNum   = regexp.MustCompile(`\D`)
	rutaImg   = regexp.MustCompile(`^/api/img/(\d+)\.png$`)
)

func cargar() {
	os.MkdirAll(dirImg, 0o755)
	b, err := os.ReadFile(archivoDB)
	if err != nil {
		return
	}
	var d struct {
		Registros    []Registro     `json:"registros"`
		Dispositivos []*Dispositivo `json:"dispositivos"`
		Cuenta       map[string]int `json:"cuenta"`
	}
	if json.Unmarshal(b, &d) == nil {
		registros = d.Registros
		for _, x := range d.Dispositivos {
			disps[x.ID] = x
		}
		if d.Cuenta != nil {
			cuenta = d.Cuenta
		}
	}
	for _, r := range registros {
		if r.UID != "" {
			uids[r.UID] = r.Folio
		}
	}
}

func guardar() {
	lista := make([]*Dispositivo, 0, len(disps))
	for _, x := range disps {
		lista = append(lista, x)
	}
	b, _ := json.MarshalIndent(map[string]any{"registros": registros, "dispositivos": lista, "cuenta": cuenta}, "", " ")
	tmp := archivoDB + ".tmp"
	if os.WriteFile(tmp, b, 0o644) == nil {
		os.Rename(tmp, archivoDB) // en Windows reemplaza el archivo existente
	}
	// Respaldo extra: CSV que se abre directo en Excel
	var sb strings.Builder
	sb.WriteString("\ufeffFolio,Nombre,Nombre escrito a mano,Telefono,Representante de casilla,Fecha y hora,Registrado en\r\n")
	for _, r := range registros {
		escrito := ""
		if r.Firma {
			escrito = "imagenes\\" + strconv.Itoa(r.Folio) + ".png"
		}
		fecha := r.Fecha
		if t, err := time.Parse(time.RFC3339Nano, r.Fecha); err == nil {
			fecha = t.Local().Format("02/01/2006 15:04")
		}
		nombre, tel := r.Nombre, csvCampo("=\""+r.Telefono+"\"")
		if nombre == "" && !r.Firma {
			nombre = "(omitido)"
		}
		if r.Telefono == "" {
			tel = "(omitido)"
		}
		fmt.Fprintf(&sb, "%d,%s,%s,%s,%s,%s,%s\r\n", r.Folio, csvCampo(nombre), escrito, tel, csvCampo(r.Rep), fecha, csvCampo(nombreDisp(r.Disp)))
	}
	tmpc := filepath.Join(dirDatos, "registros.csv.tmp")
	if os.WriteFile(tmpc, []byte(sb.String()), 0o644) == nil {
		if os.Rename(tmpc, filepath.Join(dirDatos, "registros.csv")) != nil {
			os.Remove(tmpc) // si Excel tiene el CSV abierto, se actualiza la proxima vez
		}
	}
}

func nombreDisp(id string) string {
	if d, ok := disps[id]; ok {
		return d.Nombre
	}
	return ""
}

// tocar registra que un dispositivo esta conectado. Se llama con mu tomado.
func tocar(id, tipo string, r *http.Request) {
	id = corta(id, 40)
	if id == "" {
		return
	}
	d, ok := disps[id]
	if !ok {
		host, _, _ := net.SplitHostPort(r.RemoteAddr)
		if ip := net.ParseIP(host); ip != nil && ip.IsLoopback() {
			d = &Dispositivo{ID: id, Nombre: "Esta computadora"}
		} else {
			if tipo != "Tableta" && tipo != "Celular" && tipo != "Computadora" {
				tipo = "Dispositivo"
			}
			cuenta[tipo]++
			d = &Dispositivo{ID: id, Nombre: fmt.Sprintf("%s %d", tipo, cuenta[tipo])}
		}
		disps[id] = d
		guardar()
		fmt.Printf("  [NUEVO DISPOSITIVO] %s\n", d.Nombre)
	}
	d.Ultima = time.Now()
}

func csvCampo(s string) string {
	return `"` + strings.ReplaceAll(s, `"`, `""`) + `"`
}

func responderJSON(w http.ResponseWriter, code int, v any) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.Header().Set("Cache-Control", "no-store")
	w.WriteHeader(code)
	json.NewEncoder(w).Encode(v)
}

func corta(s string, n int) string {
	r := []rune(s)
	if len(r) > n {
		return string(r[:n])
	}
	return s
}

func ipsLocales() []string {
	var out []string
	ifs, _ := net.Interfaces()
	for _, i := range ifs {
		if i.Flags&net.FlagUp == 0 || i.Flags&net.FlagLoopback != 0 {
			continue
		}
		addrs, _ := i.Addrs()
		for _, a := range addrs {
			if ipn, ok := a.(*net.IPNet); ok {
				if ip4 := ipn.IP.To4(); ip4 != nil && !ip4.IsLinkLocalUnicast() {
					out = append(out, ip4.String())
				}
			}
		}
	}
	return out
}

func handler(w http.ResponseWriter, r *http.Request) {
	p := r.URL.Path
	if r.Method == http.MethodGet {
		switch {
		case p == "/" || p == "/index.html" || p == "/registro-evento.html":
			w.Header().Set("Content-Type", "text/html; charset=utf-8")
			w.Header().Set("Cache-Control", "no-store")
			w.Write(pagina)
		case p == "/api/registros":
			mu.Lock()
			defer mu.Unlock()
			tocar(r.URL.Query().Get("d"), r.URL.Query().Get("t"), r)
			if r.URL.Query().Get("v") == strconv.FormatInt(version, 10) {
				responderJSON(w, 200, map[string]any{"changed": false, "version": version})
				return
			}
			pub := make([]map[string]any, 0, len(registros))
			for _, x := range registros {
				pub = append(pub, map[string]any{"folio": x.Folio, "nombre": x.Nombre, "telefono": x.Telefono, "fecha": x.Fecha, "firma": x.Firma, "representante": x.Rep, "dispNombre": nombreDisp(x.Disp)})
			}
			responderJSON(w, 200, map[string]any{"changed": true, "version": version, "registros": pub})
		case p == "/api/dispositivos":
			mu.Lock()
			defer mu.Unlock()
			porDisp := map[string]int{}
			for _, x := range registros {
				porDisp[x.Disp]++
			}
			lista := []map[string]any{}
			conectados := 0
			for _, d := range disps {
				if d.Ultima.IsZero() {
					continue // visto antes de reiniciar el programa y no ha vuelto
				}
				hace := int(time.Since(d.Ultima).Seconds())
				on := hace < 10
				if on {
					conectados++
				}
				lista = append(lista, map[string]any{"nombre": d.Nombre, "conectado": on, "hace": hace, "registros": porDisp[d.ID]})
			}
			sort.Slice(lista, func(i, j int) bool { return lista[i]["nombre"].(string) < lista[j]["nombre"].(string) })
			responderJSON(w, 200, map[string]any{"conectados": conectados, "dispositivos": lista})
		case p == "/api/info":
			urls := []string{}
			for _, ip := range ipsLocales() {
				urls = append(urls, fmt.Sprintf("http://%s:%d", ip, puerto))
			}
			responderJSON(w, 200, map[string]any{"urls": urls})
		case rutaImg.MatchString(p):
			m := rutaImg.FindStringSubmatch(p)
			b, err := os.ReadFile(filepath.Join(dirImg, m[1]+".png"))
			if err != nil {
				responderJSON(w, 404, map[string]string{"error": "no encontrado"})
				return
			}
			w.Header().Set("Content-Type", "image/png")
			w.Header().Set("Cache-Control", "no-store")
			w.Write(b)
		default:
			responderJSON(w, 404, map[string]string{"error": "no encontrado"})
		}
		return
	}
	if r.Method != http.MethodPost {
		responderJSON(w, 405, map[string]string{"error": "metodo"})
		return
	}
	r.Body = http.MaxBytesReader(w, r.Body, 3_000_000)
	var body map[string]any
	if err := json.NewDecoder(r.Body).Decode(&body); err != nil {
		responderJSON(w, 400, map[string]string{"error": "json"})
		return
	}
	str := func(k string) string { s, _ := body[k].(string); return s }

	switch p {
	case "/api/registro":
		uid := corta(str("uid"), 40)
		nombre := corta(str("nombre"), 150)
		tel := corta(soloNum.ReplaceAllString(str("telefono"), ""), 15)
		fecha := corta(str("fecha"), 40)
		img := str("img")
		disp := corta(str("disp"), 40)
		repAns := corta(str("representante"), 5)
		mu.Lock()
		tocar(disp, str("tipo"), r)
		if f, ok := uids[uid]; uid != "" && ok {
			mu.Unlock()
			responderJSON(w, 200, map[string]int{"folio": f})
			return
		}
		folio := 1
		for _, x := range registros {
			if x.Folio >= folio {
				folio = x.Folio + 1
			}
		}
		firma := false
		if strings.HasPrefix(img, "data:image/png;base64,") {
			if b, err := base64.StdEncoding.DecodeString(img[len("data:image/png;base64,"):]); err == nil {
				if os.WriteFile(filepath.Join(dirImg, strconv.Itoa(folio)+".png"), b, 0o644) == nil {
					firma = true
				}
			}
		}
		registros = append(registros, Registro{folio, nombre, tel, fecha, firma, uid, disp, repAns})
		if uid != "" {
			uids[uid] = folio
		}
		version++
		guardar()
		total := len(registros)
		mu.Unlock()
		n := nombre
		if n == "" && firma {
			n = "(escrito a mano)"
		} else if n == "" {
			n = "(omitido)"
		}
		fmt.Printf("  [OK] #%-4d %-35s %s   total: %d\n", folio, n, tel, total)
		responderJSON(w, 200, map[string]int{"folio": folio})

	case "/api/borrar":
		f, ok := body["folio"].(float64)
		if !ok {
			responderJSON(w, 400, map[string]string{"error": "folio"})
			return
		}
		folio := int(f)
		mu.Lock()
		out := registros[:0]
		for _, x := range registros {
			if x.Folio != folio {
				out = append(out, x)
			}
		}
		registros = out
		os.Remove(filepath.Join(dirImg, strconv.Itoa(folio)+".png"))
		version++
		guardar()
		mu.Unlock()
		fmt.Printf("  [BORRADO] #%d\n", folio)
		responderJSON(w, 200, map[string]bool{"ok": true})

	case "/api/borrar-todo":
		mu.Lock()
		ts := time.Now().Format("20060102_150405")
		if len(registros) > 0 {
			if b, err := os.ReadFile(archivoDB); err == nil {
				os.WriteFile(filepath.Join(dirDatos, "respaldo_"+ts+".json"), b, 0o644)
			}
			os.Rename(dirImg, filepath.Join(dirDatos, "imagenes_respaldo_"+ts))
			os.MkdirAll(dirImg, 0o755)
		}
		registros = nil
		uids = map[string]int{}
		version++
		guardar()
		mu.Unlock()
		fmt.Printf("  [BORRADO TODO] respaldo en registros\\respaldo_%s.json\n", ts)
		responderJSON(w, 200, map[string]bool{"ok": true})

	default:
		responderJSON(w, 404, map[string]string{"error": "no encontrado"})
	}
}

func abrirNavegador(url string) {
	switch runtime.GOOS {
	case "windows":
		exec.Command("rundll32", "url.dll,FileProtocolHandler", url).Start()
	case "darwin":
		exec.Command("open", url).Start()
	default:
		exec.Command("xdg-open", url).Start()
	}
}

func esperarEnter() {
	fmt.Println("\nPresiona Enter para cerrar...")
	fmt.Scanln()
}

func main() {
	exe, _ := os.Executable()
	base := filepath.Dir(exe)
	if d := os.Getenv("REGISTRO_DIR"); d != "" {
		base = d
	}
	dirDatos = filepath.Join(base, "registros")
	dirImg = filepath.Join(dirDatos, "imagenes")
	archivoDB = filepath.Join(dirDatos, "datos.json")
	cargar()

	ln, err := net.Listen("tcp", fmt.Sprintf("0.0.0.0:%d", puerto))
	if err != nil {
		fmt.Printf("El puerto %d esta ocupado. Quiza el programa ya esta abierto en otra ventana.\n", puerto)
		esperarEnter()
		return
	}
	linea := strings.Repeat("=", 62)
	fmt.Println(linea)
	fmt.Println("   REGISTRO DEL EVENTO - ENCENDIDO   (NO CIERRES ESTA VENTANA)")
	fmt.Println(linea)
	fmt.Printf("   Registros guardados: %d\n", len(registros))
	fmt.Println("   En la TABLETA abre Chrome y escribe:")
	ips := ipsLocales()
	if len(ips) == 0 {
		fmt.Println("        (sin red: conecta esta computadora al WiFi / hotspot)")
	}
	for _, ip := range ips {
		fmt.Printf("        http://%s:%d\n", ip, puerto)
	}
	fmt.Println("   En esta computadora el panel se abre solo (PIN 2811).")
	fmt.Println("   Los datos se guardan en la carpeta 'registros'.")
	fmt.Println(linea)
	if os.Getenv("REGISTRO_NO_BROWSER") == "" {
		go func() { time.Sleep(time.Second); abrirNavegador(fmt.Sprintf("http://localhost:%d/#panel", puerto)) }()
	}
	if err := http.Serve(ln, http.HandlerFunc(handler)); err != nil {
		fmt.Println("Error:", err)
		esperarEnter()
	}
}
