package main

import (
	"bufio"
	"bytes"
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"text/template"
)

func main() {
	if len(os.Args) > 1 {
		switch os.Args[1] {
		case "init":
			initProject()
			return
		case "generate":
			generateEntity()
			return
		}
	}

	// Interactive menu
	reader := bufio.NewReader(os.Stdin)
	fmt.Println("go-clean-template bootstrap CLI")
	fmt.Println("━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━")
	fmt.Println("1) init    — Rename module and initialize a new project")
	fmt.Println("2) generate — Scaffold a new CRUD entity")
	fmt.Println()
	fmt.Print("Choose [1-2]: ")

	choice, _ := reader.ReadString('\n')
	choice = strings.TrimSpace(choice)

	switch choice {
	case "1":
		initProject()
	case "2":
		generateEntity()
	default:
		fmt.Println("Invalid choice. Run with 'init' or 'generate' subcommand.")
		os.Exit(1)
	}
}

// ── shared helpers ────────────────────────────────────────────────────────────

func prompt(label, defaultVal string) string {
	reader := bufio.NewReader(os.Stdin)
	prompt := fmt.Sprintf("%s [%s]: ", label, defaultVal)
	fmt.Print(prompt)
	input, _ := reader.ReadString('\n')
	input = strings.TrimSpace(input)
	if input == "" {
		return defaultVal
	}
	return input
}

func readModule() string {
	data, err := os.ReadFile("go.mod")
	if err != nil {
		fmt.Fprintf(os.Stderr, "cannot read go.mod: %v\n", err)
		os.Exit(1)
	}
	for _, line := range strings.Split(string(data), "\n") {
		if strings.HasPrefix(line, "module ") {
			return strings.TrimSpace(strings.TrimPrefix(line, "module "))
		}
	}
	fmt.Fprintln(os.Stderr, "module directive not found in go.mod")
	os.Exit(1)
	return ""
}

var moduleCache string

func currentModule() string {
	if moduleCache == "" {
		moduleCache = readModule()
	}
	return moduleCache
}

// toPascal converts "product_category" or "product" to "ProductCategory".
func toPascal(s string) string {
	parts := strings.FieldsFunc(s, func(r rune) bool { return r == '_' || r == '-' || r == ' ' })
	for i, p := range parts {
		if len(p) > 0 {
			parts[i] = strings.ToUpper(p[:1]) + p[1:]
		}
	}
	return strings.Join(parts, "")
}

// toCamel converts "product_category" to "productCategory".
func toCamel(s string) string {
	p := toPascal(s)
	if len(p) > 0 {
		return strings.ToLower(p[:1]) + p[1:]
	}
	return p
}

func pluralize(s string) string {
	if strings.HasSuffix(s, "s") || strings.HasSuffix(s, "x") || strings.HasSuffix(s, "ch") || strings.HasSuffix(s, "sh") {
		return s + "es"
	}
	if strings.HasSuffix(s, "y") && len(s) > 2 &&
		!strings.Contains("aeiou", string(s[len(s)-2])) {
		return s[:len(s)-1] + "ies"
	}
	return s + "s"
}

// entityNaming derives all naming forms from the singular entity name.
type entityNaming struct {
	Singular     string // PascalCase singular: "Product"
	SingularVar  string // camelCase singular: "product"
	Plural       string // PascalCase plural: "Products"
	PluralVar    string // camelCase plural: "products"
	Path         string // URL path: "products"
	Package      string // Go package name: "product"
	SingularUser string // user-provided raw input
	PluralUser   string // user-provided plural raw input
}

func deriveNaming(rawSingular, rawPlural string) entityNaming {
	s := strings.ToLower(strings.TrimSpace(rawSingular))
	p := strings.ToLower(strings.TrimSpace(rawPlural))
	if p == "" {
		p = pluralize(s)
	}

	return entityNaming{
		Singular:     toPascal(s),
		SingularVar:  toCamel(s),
		Plural:       toPascal(p),
		PluralVar:    toCamel(p),
		Path:         p,
		Package:      s,
		SingularUser: s,
		PluralUser:   p,
	}
}

// ── init command ──────────────────────────────────────────────────────────────

func initProject() {
	oldMod := currentModule()
	fmt.Printf("Current module: %s\n", oldMod)
	newMod := prompt("New module name", oldMod)
	if newMod == oldMod {
		fmt.Println("Module name unchanged, nothing to do.")
		return
	}

	// Confirm
	fmt.Printf("Rename module from %q to %q?\n", oldMod, newMod)
	fmt.Print("Continue? [Y/n]: ")
	reader := bufio.NewReader(os.Stdin)
	confirm, _ := reader.ReadString('\n')
	confirm = strings.TrimSpace(strings.ToLower(confirm))
	if confirm == "n" || confirm == "no" {
		fmt.Println("Cancelled.")
		return
	}

	// 1. Update go.mod
	modData, err := os.ReadFile("go.mod")
	if err != nil {
		fmt.Fprintf(os.Stderr, "error reading go.mod: %v\n", err)
		os.Exit(1)
	}
	updated := strings.ReplaceAll(string(modData), oldMod, newMod)
	if err := os.WriteFile("go.mod", []byte(updated), 0644); err != nil {
		fmt.Fprintf(os.Stderr, "error writing go.mod: %v\n", err)
		os.Exit(1)
	}
	fmt.Println("✓ Updated go.mod")

	// 2. Replace in all .go files and other text files
	count := 0
	extensions := []string{".go", ".md", ".yaml", ".yml", ".json", ".toml"}
	skipDirs := map[string]bool{".git": true, "bin": true, "tmp": true, ".tools": true}

	filepath.Walk(".", func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		if info.IsDir() && skipDirs[info.Name()] {
			return filepath.SkipDir
		}
		if info.IsDir() {
			return nil
		}

		ext := filepath.Ext(path)
		hasExt := false
		for _, e := range extensions {
			if ext == e {
				hasExt = true
				break
			}
		}
		if !hasExt {
			return nil
		}

		data, err := os.ReadFile(path)
		if err != nil {
			return nil
		}
		if !strings.Contains(string(data), oldMod) {
			return nil
		}
		newData := strings.ReplaceAll(string(data), oldMod, newMod)
		if err := os.WriteFile(path, []byte(newData), info.Mode()); err != nil {
			return nil
		}
		count++
		return nil
	})

	fmt.Printf("✓ Updated %d files\n", count)
	fmt.Println("Done. Run 'go mod tidy' to clean up dependencies.")
}

// ── generate command ──────────────────────────────────────────────────────────

// entityTemplateData is the context passed to all templates.
type entityTemplateData struct {
	Module        string
	Entity        string // Product
	EntityVar     string // product
	Entities      string // Products
	EntitiesVar   string // products
	Path          string // products
	Package       string // product (Go package name for usecase subdir)
}

func generateEntity() {
	module := currentModule()

	reader := bufio.NewReader(os.Stdin)
	fmt.Print("Entity name (singular, e.g. product): ")
	singular, _ := reader.ReadString('\n')
	singular = strings.TrimSpace(singular)
	if singular == "" {
		fmt.Println("Entity name is required.")
		os.Exit(1)
	}

	defaultPlural := pluralize(singular)
	fmt.Printf("Plural name [%s]: ", defaultPlural)
	pluralInput, _ := reader.ReadString('\n')
	pluralInput = strings.TrimSpace(pluralInput)
	if pluralInput == "" {
		pluralInput = defaultPlural
	}

	n := deriveNaming(singular, pluralInput)
	data := entityTemplateData{
		Module:      module,
		Entity:      n.Singular,
		EntityVar:   n.SingularVar,
		Entities:    n.Plural,
		EntitiesVar: n.PluralVar,
		Path:        n.Path,
		Package:     n.Package,
	}

	fmt.Printf("\nGenerating %s entity...\n\n", data.Entity)

	// Generate files
	genFiles := map[string]string{
		// Domain
		fmt.Sprintf("internal/domain/%s.go", data.Package):                     tmplDomain,
		// Use cases
		fmt.Sprintf("internal/application/usecase/%s/create.go", data.Package): tmplCreateUC,
		fmt.Sprintf("internal/application/usecase/%s/get.go", data.Package):    tmplGetUC,
		fmt.Sprintf("internal/application/usecase/%s/list.go", data.Package):   tmplListUC,
		fmt.Sprintf("internal/application/usecase/%s/update.go", data.Package): tmplUpdateUC,
		fmt.Sprintf("internal/application/usecase/%s/delete.go", data.Package): tmplDeleteUC,
		// DTO
		fmt.Sprintf("internal/interface/dto/%s.go", data.Package): tmplDTO,
		// Handler
		fmt.Sprintf("internal/interface/handler/%s.go", data.Package): tmplHandler,
		// Persistence
		fmt.Sprintf("internal/infrastructure/persistence/%s.go", data.Package): tmplRepo,
		// Use case tests
		fmt.Sprintf("tests/application/usecase/%s/create_test.go", data.Package): tmplCreateTest,
		fmt.Sprintf("tests/application/usecase/%s/get_test.go", data.Package):    tmplGetTest,
		fmt.Sprintf("tests/application/usecase/%s/list_test.go", data.Package):   tmplListTest,
		fmt.Sprintf("tests/application/usecase/%s/update_test.go", data.Package): tmplUpdateTest,
		fmt.Sprintf("tests/application/usecase/%s/delete_test.go", data.Package): tmplDeleteTest,
		fmt.Sprintf("tests/application/usecase/%s/mocks_test.go", data.Package):  tmplMocksTest,
		// Handler test
		fmt.Sprintf("tests/interface/handler/%s_test.go", data.Package): tmplHandlerTest,
	}

	for path, tmpl := range genFiles {
		renderFile(path, tmpl, data)
	}

	// Modify existing files
	editCmdMain(data)
	editRouter(data)
	editSeed(data)
	editHandlerHelpers(data)
	editSeedMain(data)

	fmt.Println("\n✓ Entity generation complete!")
	fmt.Println("Run 'go mod tidy' then 'make test' to verify.")
	showPostGenSteps(data)
}

func renderFile(path, tmpl string, data entityTemplateData) {
	dir := filepath.Dir(path)
	if err := os.MkdirAll(dir, 0755); err != nil {
		fmt.Fprintf(os.Stderr, "error creating directory %s: %v\n", dir, err)
		os.Exit(1)
	}

	if _, err := os.Stat(path); err == nil {
		fmt.Printf("  ⚠ %s already exists, skipping\n", path)
		return
	}

	funcMap := template.FuncMap{
		"bt": func() string { return "`" },
	}
	t, err := template.New(filepath.Base(path)).Funcs(funcMap).Parse(tmpl)
	if err != nil {
		fmt.Fprintf(os.Stderr, "error parsing template for %s: %v\n", path, err)
		os.Exit(1)
	}

	var buf bytes.Buffer
	if err := t.Execute(&buf, data); err != nil {
		fmt.Fprintf(os.Stderr, "error executing template for %s: %v\n", path, err)
		os.Exit(1)
	}

	if err := os.WriteFile(path, buf.Bytes(), 0644); err != nil {
		fmt.Fprintf(os.Stderr, "error writing %s: %v\n", path, err)
		os.Exit(1)
	}
	fmt.Printf("  ✓ Created %s\n", path)
}

func editCmdMain(data entityTemplateData) {
	path := "cmd/main.go"
	src, err := os.ReadFile(path)
	if err != nil {
		fmt.Fprintf(os.Stderr, "error reading %s: %v\n", path, err)
		return
	}
	content := string(src)

	mod := currentModule()
	ucImport := fmt.Sprintf("\t%susecase \"%s/internal/application/usecase/%s\"", data.Package, mod, data.Package)

	// Add import
	if !strings.Contains(content, ucImport) {
		// Find the last use case import and add after it
		lastUCImport := fmt.Sprintf("\troleusecase \"%s/internal/application/usecase/role\"", mod)
		content = strings.Replace(content, lastUCImport, lastUCImport+"\n"+ucImport, 1)
	}

	// Add repo construction (before "// --- Use Cases ---")
	repoLine := fmt.Sprintf("\t%sRepo := persistence.New%sRepository()", data.EntityVar, data.Entity)
	content = strings.Replace(content, "\troleRepo := persistence.NewRoleRepository()",
		"\troleRepo := persistence.NewRoleRepository()\n"+repoLine, 1)

	// Add use case vars (after role use cases, before "// --- Handlers ---")
	ucLines := ""
	for _, op := range []string{"create", "get", "list", "update", "delete"} {
		constructor := fmt.Sprintf("New%s%sUseCase", strings.ToUpper(op[:1])+op[1:], data.Entity)
		if op == "list" {
			constructor = fmt.Sprintf("NewList%sUseCase", data.Entities)
		}
		ucLines += fmt.Sprintf("\t%s%sUC := %susecase.%s(%sRepo)\n", op, data.Entity, data.Package, constructor, data.EntityVar)
	}
	content = strings.Replace(content, "\t// --- Handlers ---", ucLines+"\n\t// --- Handlers ---", 1)

	// Add handler construction
	handlerVars := ""
	for _, op := range []string{"create", "get", "list", "update", "delete"} {
		handlerVars += fmt.Sprintf("%s%sUC, ", op, data.Entity)
	}
	handlerVars = strings.TrimSuffix(handlerVars, ", ")
	handlerLine := fmt.Sprintf("\t%sHandler := handler.New%sHandler(\n\t\t%s,\n\t)", data.Entity, data.Entity, handlerVars)

	// Find the last handler construction and add after it
	lastHandler := "\t)"
	roleHandlerEnd := strings.Index(content, lastHandler)
	if roleHandlerEnd > 0 {
		// Find the last occurrence of ")" closing a handler call
		lastHandlerPos := strings.LastIndex(content, "\t)")
		content = content[:lastHandlerPos+2] + "\n\n"+handlerLine + content[lastHandlerPos+2:]
	}

	// Add repo parameter to seed.Run call
	oldSeed := fmt.Sprintf("seed.Run(context.Background(), log, roleRepo, userRepo)")
	newSeed := fmt.Sprintf("seed.Run(context.Background(), log, roleRepo, userRepo, %sRepo)", data.EntityVar)
	content = strings.Replace(content, oldSeed, newSeed, 1)

	// Add to router.New call
	routerCall := fmt.Sprintf("router.New(log, cfg.CORSOrigin, userHandler, roleHandler)")
	routerReplace := fmt.Sprintf("router.New(log, cfg.CORSOrigin, userHandler, roleHandler, %sHandler)", data.Entity)
	content = strings.Replace(content, routerCall, routerReplace, 1)

	if err := os.WriteFile(path, []byte(content), 0644); err != nil {
		fmt.Fprintf(os.Stderr, "error writing %s: %v\n", path, err)
		return
	}
	fmt.Printf("  ✓ Updated %s\n", path)
}

func editRouter(data entityTemplateData) {
	path := "internal/interface/router/router.go"
	src, err := os.ReadFile(path)
	if err != nil {
		fmt.Fprintf(os.Stderr, "error reading %s: %v\n", path, err)
		return
	}
	content := string(src)

	// Add handler parameter to New function
	oldNewSig := fmt.Sprintf("userHandler *handler.UserHandler,\n\troleHandler *handler.RoleHandler,\n) http.Handler")
	newNewSig := fmt.Sprintf("userHandler *handler.UserHandler,\n\troleHandler *handler.RoleHandler,\n\t%sHandler *handler.%sHandler,\n) http.Handler", data.Entity, data.Entity)
	content = strings.Replace(content, oldNewSig, newNewSig, 1)

	// Add routes
	routeBlock := fmt.Sprintf(`
		r.Route("/%s", func(r chi.Router) {
			r.Get("/", %sHandler.GetAll)
			r.Post("/", %sHandler.Create)
			r.Get("/{id}", %sHandler.GetByID)
			r.Put("/{id}", %sHandler.Update)
			r.Delete("/{id}", %sHandler.Delete)
		})`, data.Path, data.Entity, data.Entity, data.Entity, data.Entity, data.Entity)

	// Insert before the closing of /api/v1 route block (before the last })
	lastBrace := strings.LastIndex(content, "\t})")
	if lastBrace > 0 {
		content = content[:lastBrace] + routeBlock + "\n" + content[lastBrace:]
	}

	if err := os.WriteFile(path, []byte(content), 0644); err != nil {
		fmt.Fprintf(os.Stderr, "error writing %s: %v\n", path, err)
		return
	}
	fmt.Printf("  ✓ Updated %s\n", path)
}

func editSeed(data entityTemplateData) {
	path := "internal/infrastructure/seed/seed.go"
	src, err := os.ReadFile(path)
	if err != nil {
		fmt.Fprintf(os.Stderr, "error reading %s: %v\n", path, err)
		return
	}
	content := string(src)

	// Add repo parameter to Run function
	oldRunSig := "func Run(\n\tctx context.Context, log *slog.Logger,\n\troleRepo domain.RoleRepository,\n\tuserRepo domain.UserRepository,\n)"
	newRunSig := fmt.Sprintf("func Run(\n\tctx context.Context, log *slog.Logger,\n\troleRepo domain.RoleRepository,\n\tuserRepo domain.UserRepository,\n\t%sRepo domain.%sRepository,\n)", data.EntityVar, data.Entity)
	content = strings.Replace(content, oldRunSig, newRunSig, 1)

	// Add seed call in Run body
	seedCall := fmt.Sprintf("\tseed%s(ctx, log, %sRepo)", data.Entities, data.EntityVar)
	// Find the last seed call line and add after
	lastSeedCall := "\tseedUsers(ctx, log, userRepo, roleRepo)"
	content = strings.Replace(content, lastSeedCall, lastSeedCall+"\n"+seedCall, 1)

	// Add seed function
	seedFunc := fmt.Sprintf(`
func seed%[1]s(ctx context.Context, log *slog.Logger, repo domain.%[2]sRepository) {
	existing, _, _ := repo.FindAll(ctx, 0, 1)
	if len(existing) > 0 {
		log.Info("%[3]ss already seeded, skipping")
		return
	}

	%[4]ss := []struct {
		name        string
		description string
	}{
		{"sample-%[3]s", "A sample %[3]s"},
	}

	for _, e := range %[4]ss {
		entity, err := domain.New%[2]s(e.name, e.description)
		if err != nil {
			log.Error("invalid %[3]s", "name", e.name, "error", err)
			continue
		}
		if err := repo.Create(ctx, entity); err != nil {
			log.Error("failed to seed %[3]s", "name", e.name, "error", err)
			continue
		}
		log.Info("seeded %[3]s", "name", e.name)
	}
}`, data.Entities, data.Entity, data.EntityVar, data.Package)

	content += seedFunc

	if err := os.WriteFile(path, []byte(content), 0644); err != nil {
		fmt.Fprintf(os.Stderr, "error writing %s: %v\n", path, err)
		return
	}
	fmt.Printf("  ✓ Updated %s\n", path)
}

func editHandlerHelpers(data entityTemplateData) {
	path := "internal/interface/handler/helpers.go"
	src, err := os.ReadFile(path)
	if err != nil {
		fmt.Fprintf(os.Stderr, "error reading %s: %v\n", path, err)
		return
	}
	content := string(src)

	helperFunc := fmt.Sprintf(`
func to%sResponse(entity *domain.%s) *dto.%sResponse {
	return &dto.%sResponse{
		ID:          entity.ID,
		Name:        entity.Name,
		Description: entity.Description,
		CreatedAt:   entity.CreatedAt.Format(time.RFC3339),
		UpdatedAt:   entity.UpdatedAt.Format(time.RFC3339),
	}
}`, data.Entity, data.Entity, data.Entity, data.Entity)

	content += helperFunc

	if err := os.WriteFile(path, []byte(content), 0644); err != nil {
		fmt.Fprintf(os.Stderr, "error writing %s: %v\n", path, err)
		return
	}
	fmt.Printf("  ✓ Updated %s\n", path)
}

func editSeedMain(data entityTemplateData) {
	path := "cmd/seed/main.go"
	src, err := os.ReadFile(path)
	if err != nil {
		fmt.Fprintf(os.Stderr, "error reading %s: %v\n", path, err)
		return
	}
	content := string(src)

	// Add repo construction
	repoLine := fmt.Sprintf("\t%sRepo := persistence.New%sRepository()", data.EntityVar, data.Entity)
	content = strings.Replace(content, "\tuserRepo := persistence.NewUserRepository()",
		"\tuserRepo := persistence.NewUserRepository()\n"+repoLine, 1)

	// Add repo to seed.Run call
	oldSeed := "seed.Run(context.Background(), log, roleRepo, userRepo)"
	newSeed := fmt.Sprintf("seed.Run(context.Background(), log, roleRepo, userRepo, %sRepo)", data.EntityVar)
	content = strings.Replace(content, oldSeed, newSeed, 1)

	if err := os.WriteFile(path, []byte(content), 0644); err != nil {
		fmt.Fprintf(os.Stderr, "error writing %s: %v\n", path, err)
		return
	}
	fmt.Printf("  ✓ Updated %s\n", path)
}

func showPostGenSteps(data entityTemplateData) {
	fmt.Println()
	fmt.Println("Post-generation steps:")
	fmt.Printf("  1. Run 'go mod tidy'\n")
	fmt.Printf("  2. Run 'make test' to verify\n")
	fmt.Printf("  3. Run 'make run' and test /api/v1/%s endpoints\n", data.Path)
}

// ── Templates ─────────────────────────────────────────────────────────────────

const tmplDomain = `package domain

import (
	"context"
	"strings"
	"time"
)

type {{.Entity}} struct {
	ID          string
	Name        string
	Description string
	CreatedAt   time.Time
	UpdatedAt   time.Time
}

func New{{.Entity}}(name, description string) (*{{.Entity}}, error) {
	e := &{{.Entity}}{
		ID:          GenerateID(),
		Name:        name,
		Description: description,
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}
	if err := e.Validate(); err != nil {
		return nil, err
	}
	return e, nil
}

func (e *{{.Entity}}) UpdateInfo(name, description string) error {
	e.Name = name
	e.Description = description
	e.UpdatedAt = time.Now()
	return e.Validate()
}

func (e *{{.Entity}}) Validate() error {
	var errs []string
	if strings.TrimSpace(e.Name) == "" {
		errs = append(errs, "name is required")
	}
	if len(errs) > 0 {
		return &DomainError{
			Code:    "VALIDATION_ERROR",
			Message: strings.Join(errs, "; "),
			Err:     ErrInvalidInput,
		}
	}
	return nil
}

type {{.Entity}}Repository interface {
	FindByID(ctx context.Context, id string) (*{{.Entity}}, error)
	FindAll(ctx context.Context, offset, limit int) ([]*{{.Entity}}, int64, error)
	FindByName(ctx context.Context, name string) (*{{.Entity}}, error)
	Create(ctx context.Context, entity *{{.Entity}}) error
	Update(ctx context.Context, entity *{{.Entity}}) error
	Delete(ctx context.Context, id string) error
}
`

const tmplCreateUC = `package {{.Package}}

import (
	"context"

	"{{.Module}}/internal/domain"
)

type Create{{.Entity}}Input struct {
	Name        string
	Description string
}

type Create{{.Entity}}Output struct {
	{{.Entity}} *domain.{{.Entity}}
}

type Create{{.Entity}}UseCase interface {
	Execute(ctx context.Context, input *Create{{.Entity}}Input) (*Create{{.Entity}}Output, error)
}

type create{{.Entity}}UseCase struct {
	repo domain.{{.Entity}}Repository
}

func NewCreate{{.Entity}}UseCase(repo domain.{{.Entity}}Repository) Create{{.Entity}}UseCase {
	return &create{{.Entity}}UseCase{repo: repo}
}

func (uc *create{{.Entity}}UseCase) Execute(ctx context.Context, input *Create{{.Entity}}Input) (*Create{{.Entity}}Output, error) {
	entity, err := domain.New{{.Entity}}(input.Name, input.Description)
	if err != nil {
		return nil, err
	}
	existing, _ := uc.repo.FindByName(ctx, input.Name)
	if existing != nil {
		return nil, domain.ErrAlreadyExists
	}
	if err := uc.repo.Create(ctx, entity); err != nil {
		return nil, err
	}
	return &Create{{.Entity}}Output{{"{"}}{{.Entity}}: entity}, nil
}
`

const tmplGetUC = `package {{.Package}}

import (
	"context"

	"{{.Module}}/internal/domain"
)

type Get{{.Entity}}Input struct {
	ID string
}

type Get{{.Entity}}Output struct {
	{{.Entity}} *domain.{{.Entity}}
}

type Get{{.Entity}}UseCase interface {
	Execute(ctx context.Context, input *Get{{.Entity}}Input) (*Get{{.Entity}}Output, error)
}

type get{{.Entity}}UseCase struct {
	repo domain.{{.Entity}}Repository
}

func NewGet{{.Entity}}UseCase(repo domain.{{.Entity}}Repository) Get{{.Entity}}UseCase {
	return &get{{.Entity}}UseCase{repo: repo}
}

func (uc *get{{.Entity}}UseCase) Execute(ctx context.Context, input *Get{{.Entity}}Input) (*Get{{.Entity}}Output, error) {
	entity, err := uc.repo.FindByID(ctx, input.ID)
	if err != nil {
		return nil, err
	}
	return &Get{{.Entity}}Output{{"{"}}{{.Entity}}: entity}, nil
}
`

const tmplListUC = `package {{.Package}}

import (
	"context"

	"{{.Module}}/internal/domain"
)

type List{{.Entities}}Input struct {
	Page     int
	PageSize int
}

type List{{.Entities}}Output struct {
	{{.Entities}}      []*domain.{{.Entity}}
	Total      int64
	Page       int
	PageSize   int
	TotalPages int
}

type List{{.Entities}}UseCase interface {
	Execute(ctx context.Context, input *List{{.Entities}}Input) (*List{{.Entities}}Output, error)
}

type list{{.Entities}}UseCase struct {
	repo domain.{{.Entity}}Repository
}

func NewList{{.Entities}}UseCase(repo domain.{{.Entity}}Repository) List{{.Entities}}UseCase {
	return &list{{.Entities}}UseCase{repo: repo}
}

func (uc *list{{.Entities}}UseCase) Execute(ctx context.Context, input *List{{.Entities}}Input) (*List{{.Entities}}Output, error) {
	if input.Page < 1 {
		input.Page = 1
	}
	if input.PageSize < 1 {
		input.PageSize = 20
	}
	if input.PageSize > 100 {
		input.PageSize = 100
	}
	offset := (input.Page - 1) * input.PageSize
	entities, total, err := uc.repo.FindAll(ctx, offset, input.PageSize)
	if err != nil {
		return nil, err
	}

	totalPages := int(total / int64(input.PageSize))
	if total%int64(input.PageSize) > 0 {
		totalPages++
	}
	if totalPages < 1 {
		totalPages = 1
	}

	return &List{{.Entities}}Output{
		{{.Entities}}:      entities,
		Total:      total,
		Page:       input.Page,
		PageSize:   input.PageSize,
		TotalPages: totalPages,
	}, nil
}
`

const tmplUpdateUC = `package {{.Package}}

import (
	"context"

	"{{.Module}}/internal/domain"
)

type Update{{.Entity}}Input struct {
	Name        string
	Description string
}

type Update{{.Entity}}Output struct {
	{{.Entity}} *domain.{{.Entity}}
}

type Update{{.Entity}}UseCase interface {
	Execute(ctx context.Context, id string, input *Update{{.Entity}}Input) (*Update{{.Entity}}Output, error)
}

type update{{.Entity}}UseCase struct {
	repo domain.{{.Entity}}Repository
}

func NewUpdate{{.Entity}}UseCase(repo domain.{{.Entity}}Repository) Update{{.Entity}}UseCase {
	return &update{{.Entity}}UseCase{repo: repo}
}

func (uc *update{{.Entity}}UseCase) Execute(ctx context.Context, id string, input *Update{{.Entity}}Input) (*Update{{.Entity}}Output, error) {
	entity, err := uc.repo.FindByID(ctx, id)
	if err != nil {
		return nil, err
	}
	if input.Name != entity.Name {
		existing, _ := uc.repo.FindByName(ctx, input.Name)
		if existing != nil {
			return nil, domain.ErrAlreadyExists
		}
	}
	if err := entity.UpdateInfo(input.Name, input.Description); err != nil {
		return nil, err
	}
	if err := uc.repo.Update(ctx, entity); err != nil {
		return nil, err
	}
	return &Update{{.Entity}}Output{{"{"}}{{.Entity}}: entity}, nil
}
`

const tmplDeleteUC = `package {{.Package}}

import (
	"context"

	"{{.Module}}/internal/domain"
)

type Delete{{.Entity}}Input struct {
	ID string
}

type Delete{{.Entity}}UseCase interface {
	Execute(ctx context.Context, input *Delete{{.Entity}}Input) error
}

type delete{{.Entity}}UseCase struct {
	repo domain.{{.Entity}}Repository
}

func NewDelete{{.Entity}}UseCase(repo domain.{{.Entity}}Repository) Delete{{.Entity}}UseCase {
	return &delete{{.Entity}}UseCase{repo: repo}
}

func (uc *delete{{.Entity}}UseCase) Execute(ctx context.Context, input *Delete{{.Entity}}Input) error {
	if _, err := uc.repo.FindByID(ctx, input.ID); err != nil {
		return err
	}
	return uc.repo.Delete(ctx, input.ID)
}
`

const tmplDTO = `package dto

type Create{{.Entity}}Request struct {
	Name        string ` + "`" + `json:"name"        example:"sample-{{.EntityVar}}"` + "`" + `
	Description string ` + "`" + `json:"description" example:"A sample {{.EntityVar}}"` + "`" + `
}

type Update{{.Entity}}Request struct {
	Name        string ` + "`" + `json:"name"        example:"sample-{{.EntityVar}}"` + "`" + `
	Description string ` + "`" + `json:"description" example:"A sample {{.EntityVar}}"` + "`" + `
}

type {{.Entity}}Response struct {
	ID          string ` + "`" + `json:"id"          example:"a1b2c3d4-e5f6-7890-abcd-ef1234567890"` + "`" + `
	Name        string ` + "`" + `json:"name"        example:"sample-{{.EntityVar}}"` + "`" + `
	Description string ` + "`" + `json:"description" example:"A sample {{.EntityVar}}"` + "`" + `
	CreatedAt   string ` + "`" + `json:"created_at"  example:"2024-01-01T00:00:00Z"` + "`" + `
	UpdatedAt   string ` + "`" + `json:"updated_at"  example:"2024-01-01T00:00:00Z"` + "`" + `
}

type Paginated{{.Entity}}Response struct {
	Data       []{{.Entity}}Response ` + "`" + `json:"data"` + "`" + `
	Total      int64                ` + "`" + `json:"total"` + "`" + `
	Page       int                  ` + "`" + `json:"page"` + "`" + `
	PageSize   int                  ` + "`" + `json:"page_size"` + "`" + `
	TotalPages int                  ` + "`" + `json:"total_pages"` + "`" + `
}
`

const tmplHandler = `package handler

import (
	"encoding/json"
	"net/http"

	"github.com/go-chi/chi/v5"

	{{.Package}}usecase "{{.Module}}/internal/application/usecase/{{.Package}}"
	"{{.Module}}/internal/interface/dto"
)

type {{.Entity}}Handler struct {
	create  {{.Package}}usecase.Create{{.Entity}}UseCase
	getByID {{.Package}}usecase.Get{{.Entity}}UseCase
	getAll  {{.Package}}usecase.List{{.Entities}}UseCase
	update  {{.Package}}usecase.Update{{.Entity}}UseCase
	delete  {{.Package}}usecase.Delete{{.Entity}}UseCase
}

func New{{.Entity}}Handler(
	createUC {{.Package}}usecase.Create{{.Entity}}UseCase,
	getByIDUC {{.Package}}usecase.Get{{.Entity}}UseCase,
	getAllUC {{.Package}}usecase.List{{.Entities}}UseCase,
	updateUC {{.Package}}usecase.Update{{.Entity}}UseCase,
	deleteUC {{.Package}}usecase.Delete{{.Entity}}UseCase,
) *{{.Entity}}Handler {
	return &{{.Entity}}Handler{
		create:  createUC,
		getByID: getByIDUC,
		getAll:  getAllUC,
		update:  updateUC,
		delete:  deleteUC,
	}
}

func (h *{{.Entity}}Handler) GetByID(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")
	result, err := h.getByID.Execute(r.Context(), &{{.Package}}usecase.Get{{.Entity}}Input{ID: id})
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, to{{.Entity}}Response(result.{{.Entity}}))
}

func (h *{{.Entity}}Handler) GetAll(w http.ResponseWriter, r *http.Request) {
	p := parsePagination(r)
	result, err := h.getAll.Execute(r.Context(), &{{.Package}}usecase.List{{.Entities}}Input{Page: p.Page, PageSize: p.PageSize})
	if err != nil {
		writeError(w, err)
		return
	}
	dtos := make([]*dto.{{.Entity}}Response, len(result.{{.Entities}}))
	for i, e := range result.{{.Entities}} {
		dtos[i] = to{{.Entity}}Response(e)
	}
	writeJSON(w, http.StatusOK, dto.NewPaginatedResponse(dtos, result.Total, result.Page, result.PageSize))
}

func (h *{{.Entity}}Handler) Create(w http.ResponseWriter, r *http.Request) {
	defer r.Body.Close()
	var reqDTO dto.Create{{.Entity}}Request
	if err := json.NewDecoder(r.Body).Decode(&reqDTO); err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid request body"})
		return
	}
	result, err := h.create.Execute(r.Context(), &{{.Package}}usecase.Create{{.Entity}}Input{
		Name:        reqDTO.Name,
		Description: reqDTO.Description,
	})
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusCreated, to{{.Entity}}Response(result.{{.Entity}}))
}

func (h *{{.Entity}}Handler) Update(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")
	defer r.Body.Close()
	var reqDTO dto.Update{{.Entity}}Request
	if err := json.NewDecoder(r.Body).Decode(&reqDTO); err != nil {
		writeJSON(w, http.StatusBadRequest, map[string]string{"error": "invalid request body"})
		return
	}
	result, err := h.update.Execute(r.Context(), id, &{{.Package}}usecase.Update{{.Entity}}Input{
		Name:        reqDTO.Name,
		Description: reqDTO.Description,
	})
	if err != nil {
		writeError(w, err)
		return
	}
	writeJSON(w, http.StatusOK, to{{.Entity}}Response(result.{{.Entity}}))
}

func (h *{{.Entity}}Handler) Delete(w http.ResponseWriter, r *http.Request) {
	id := chi.URLParam(r, "id")
	if err := h.delete.Execute(r.Context(), &{{.Package}}usecase.Delete{{.Entity}}Input{ID: id}); err != nil {
		writeError(w, err)
		return
	}
	w.WriteHeader(http.StatusNoContent)
}
`

const tmplRepo = `package persistence

import (
	"context"
	"sort"
	"sync"

	"{{.Module}}/internal/domain"
)

type {{.Entity}}Repository struct {
	mu        sync.RWMutex
	{{.EntitiesVar}} map[string]*domain.{{.Entity}}
}

func New{{.Entity}}Repository() *{{.Entity}}Repository {
	return &{{.Entity}}Repository{
		{{.EntitiesVar}}: make(map[string]*domain.{{.Entity}}),
	}
}

func (r *{{.Entity}}Repository) FindByID(_ context.Context, id string) (*domain.{{.Entity}}, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	entity, ok := r.{{.EntitiesVar}}[id]
	if !ok {
		return nil, domain.ErrNotFound
	}
	return entity, nil
}

func (r *{{.Entity}}Repository) FindAll(_ context.Context, offset, limit int) ([]*domain.{{.Entity}}, int64, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()

	all := make([]*domain.{{.Entity}}, 0, len(r.{{.EntitiesVar}}))
	for _, entity := range r.{{.EntitiesVar}} {
		all = append(all, entity)
	}
	sort.Slice(all, func(i, j int) bool {
		return all[i].CreatedAt.Before(all[j].CreatedAt)
	})

	total := int64(len(all))
	if offset >= len(all) {
		return nil, total, nil
	}
	end := offset + limit
	if end > len(all) {
		end = len(all)
	}
	return all[offset:end], total, nil
}

func (r *{{.Entity}}Repository) FindByName(_ context.Context, name string) (*domain.{{.Entity}}, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	for _, entity := range r.{{.EntitiesVar}} {
		if entity.Name == name {
			return entity, nil
		}
	}
	return nil, domain.ErrNotFound
}

func (r *{{.Entity}}Repository) Create(_ context.Context, entity *domain.{{.Entity}}) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	r.{{.EntitiesVar}}[entity.ID] = entity
	return nil
}

func (r *{{.Entity}}Repository) Update(_ context.Context, entity *domain.{{.Entity}}) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	if _, ok := r.{{.EntitiesVar}}[entity.ID]; !ok {
		return domain.ErrNotFound
	}
	r.{{.EntitiesVar}}[entity.ID] = entity
	return nil
}

func (r *{{.Entity}}Repository) Delete(_ context.Context, id string) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	if _, ok := r.{{.EntitiesVar}}[id]; !ok {
		return domain.ErrNotFound
	}
	delete(r.{{.EntitiesVar}}, id)
	return nil
}
`

const tmplCreateTest = `package {{.Package}}_test

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"

	{{.Package}}usecase "{{.Module}}/internal/application/usecase/{{.Package}}"
	"{{.Module}}/internal/domain"
)

func TestCreate{{.Entity}}_Success(t *testing.T) {
	mockRepo := new(Mock{{.Entity}}Repo)
	uc := {{.Package}}usecase.NewCreate{{.Entity}}UseCase(mockRepo)

	mockRepo.On("FindByName", "test-entity").Return(nil, domain.ErrNotFound)
	mockRepo.On("Create", mock.AnythingOfType("*domain.{{.Entity}}")).Return(nil)

	input := &{{.Package}}usecase.Create{{.Entity}}Input{Name: "test-entity", Description: "Test entity"}
	result, err := uc.Execute(context.Background(), input)

	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.NotNil(t, result.{{.Entity}})
	assert.Equal(t, "test-entity", result.{{.Entity}}.Name)
	assert.Equal(t, "Test entity", result.{{.Entity}}.Description)
	mockRepo.AssertExpectations(t)
}

func TestCreate{{.Entity}}_DuplicateName(t *testing.T) {
	mockRepo := new(Mock{{.Entity}}Repo)
	uc := {{.Package}}usecase.NewCreate{{.Entity}}UseCase(mockRepo)

	existing := &domain.{{.Entity}}{ID: "1", Name: "existing"}
	mockRepo.On("FindByName", "existing").Return(existing, nil)

	input := &{{.Package}}usecase.Create{{.Entity}}Input{Name: "existing", Description: "Duplicate"}
	result, err := uc.Execute(context.Background(), input)

	assert.Error(t, err)
	assert.ErrorIs(t, err, domain.ErrAlreadyExists)
	assert.Nil(t, result)
	mockRepo.AssertExpectations(t)
}

func TestCreate{{.Entity}}_InvalidInput(t *testing.T) {
	mockRepo := new(Mock{{.Entity}}Repo)
	uc := {{.Package}}usecase.NewCreate{{.Entity}}UseCase(mockRepo)

	input := &{{.Package}}usecase.Create{{.Entity}}Input{Name: "", Description: ""}
	result, err := uc.Execute(context.Background(), input)

	assert.Error(t, err)
	assert.ErrorIs(t, err, domain.ErrInvalidInput)
	assert.Nil(t, result)
}
`

const tmplGetTest = `package {{.Package}}_test

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"

	{{.Package}}usecase "{{.Module}}/internal/application/usecase/{{.Package}}"
	"{{.Module}}/internal/domain"
)

func TestGet{{.Entity}}_Success(t *testing.T) {
	mockRepo := new(Mock{{.Entity}}Repo)
	uc := {{.Package}}usecase.NewGet{{.Entity}}UseCase(mockRepo)

	mockRepo.On("FindByID", "123").Return(&domain.{{.Entity}}{ID: "123", Name: "test-entity"}, nil)

	result, err := uc.Execute(context.Background(), &{{.Package}}usecase.Get{{.Entity}}Input{ID: "123"})

	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Equal(t, "123", result.{{.Entity}}.ID)
	assert.Equal(t, "test-entity", result.{{.Entity}}.Name)
	mockRepo.AssertExpectations(t)
}

func TestGet{{.Entity}}_NotFound(t *testing.T) {
	mockRepo := new(Mock{{.Entity}}Repo)
	uc := {{.Package}}usecase.NewGet{{.Entity}}UseCase(mockRepo)

	mockRepo.On("FindByID", "999").Return(nil, domain.ErrNotFound)

	result, err := uc.Execute(context.Background(), &{{.Package}}usecase.Get{{.Entity}}Input{ID: "999"})

	assert.Error(t, err)
	assert.ErrorIs(t, err, domain.ErrNotFound)
	assert.Nil(t, result)
	mockRepo.AssertExpectations(t)
}
`

const tmplListTest = `package {{.Package}}_test

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"

	{{.Package}}usecase "{{.Module}}/internal/application/usecase/{{.Package}}"
	"{{.Module}}/internal/domain"
)

func TestList{{.Entities}}_Success(t *testing.T) {
	mockRepo := new(Mock{{.Entity}}Repo)
	uc := {{.Package}}usecase.NewList{{.Entities}}UseCase(mockRepo)

	entities := []*domain.{{.Entity}}{
		{ID: "1", Name: "First"},
		{ID: "2", Name: "Second"},
	}
	mockRepo.On("FindAll").Return(entities, nil)

	result, err := uc.Execute(context.Background(), &{{.Package}}usecase.List{{.Entities}}Input{Page: 1, PageSize: 20})

	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Len(t, result.{{.Entities}}, 2)
	assert.Equal(t, int64(2), result.Total)
	assert.Equal(t, 1, result.Page)
	assert.Equal(t, 20, result.PageSize)
	mockRepo.AssertExpectations(t)
}

func TestList{{.Entities}}_Empty(t *testing.T) {
	mockRepo := new(Mock{{.Entity}}Repo)
	uc := {{.Package}}usecase.NewList{{.Entities}}UseCase(mockRepo)

	mockRepo.On("FindAll").Return([]*domain.{{.Entity}}{}, nil)

	result, err := uc.Execute(context.Background(), &{{.Package}}usecase.List{{.Entities}}Input{Page: 1, PageSize: 20})

	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Empty(t, result.{{.Entities}})
	assert.Equal(t, int64(0), result.Total)
	mockRepo.AssertExpectations(t)
}
`

const tmplUpdateTest = `package {{.Package}}_test

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"

	{{.Package}}usecase "{{.Module}}/internal/application/usecase/{{.Package}}"
	"{{.Module}}/internal/domain"
)

func TestUpdate{{.Entity}}_Success(t *testing.T) {
	mockRepo := new(Mock{{.Entity}}Repo)
	uc := {{.Package}}usecase.NewUpdate{{.Entity}}UseCase(mockRepo)

	existing := &domain.{{.Entity}}{ID: "1", Name: "original"}
	mockRepo.On("FindByID", "1").Return(existing, nil)
	mockRepo.On("FindByName", "updated").Return(nil, domain.ErrNotFound)
	mockRepo.On("Update", mock.AnythingOfType("*domain.{{.Entity}}")).Return(nil)

	result, err := uc.Execute(context.Background(), "1", &{{.Package}}usecase.Update{{.Entity}}Input{Name: "updated", Description: "Updated entity"})

	assert.NoError(t, err)
	assert.NotNil(t, result)
	assert.Equal(t, "updated", result.{{.Entity}}.Name)
	assert.Equal(t, "Updated entity", result.{{.Entity}}.Description)
	mockRepo.AssertExpectations(t)
}

func TestUpdate{{.Entity}}_NotFound(t *testing.T) {
	mockRepo := new(Mock{{.Entity}}Repo)
	uc := {{.Package}}usecase.NewUpdate{{.Entity}}UseCase(mockRepo)

	mockRepo.On("FindByID", "999").Return(nil, domain.ErrNotFound)

	result, err := uc.Execute(context.Background(), "999", &{{.Package}}usecase.Update{{.Entity}}Input{Name: "test", Description: "test"})

	assert.Error(t, err)
	assert.ErrorIs(t, err, domain.ErrNotFound)
	assert.Nil(t, result)
	mockRepo.AssertExpectations(t)
}

func TestUpdate{{.Entity}}_DuplicateName(t *testing.T) {
	mockRepo := new(Mock{{.Entity}}Repo)
	uc := {{.Package}}usecase.NewUpdate{{.Entity}}UseCase(mockRepo)

	existing := &domain.{{.Entity}}{ID: "1", Name: "original"}
	dup := &domain.{{.Entity}}{ID: "2", Name: "taken"}
	mockRepo.On("FindByID", "1").Return(existing, nil)
	mockRepo.On("FindByName", "taken").Return(dup, nil)

	result, err := uc.Execute(context.Background(), "1", &{{.Package}}usecase.Update{{.Entity}}Input{Name: "taken", Description: "test"})

	assert.Error(t, err)
	assert.ErrorIs(t, err, domain.ErrAlreadyExists)
	assert.Nil(t, result)
	mockRepo.AssertExpectations(t)
}
`

const tmplDeleteTest = `package {{.Package}}_test

import (
	"context"
	"testing"

	"github.com/stretchr/testify/assert"

	{{.Package}}usecase "{{.Module}}/internal/application/usecase/{{.Package}}"
	"{{.Module}}/internal/domain"
)

func TestDelete{{.Entity}}_Success(t *testing.T) {
	mockRepo := new(Mock{{.Entity}}Repo)
	uc := {{.Package}}usecase.NewDelete{{.Entity}}UseCase(mockRepo)

	mockRepo.On("FindByID", "1").Return(&domain.{{.Entity}}{ID: "1", Name: "test"}, nil)
	mockRepo.On("Delete", "1").Return(nil)

	err := uc.Execute(context.Background(), &{{.Package}}usecase.Delete{{.Entity}}Input{ID: "1"})

	assert.NoError(t, err)
	mockRepo.AssertExpectations(t)
}

func TestDelete{{.Entity}}_NotFound(t *testing.T) {
	mockRepo := new(Mock{{.Entity}}Repo)
	uc := {{.Package}}usecase.NewDelete{{.Entity}}UseCase(mockRepo)

	mockRepo.On("FindByID", "999").Return(nil, domain.ErrNotFound)

	err := uc.Execute(context.Background(), &{{.Package}}usecase.Delete{{.Entity}}Input{ID: "999"})

	assert.Error(t, err)
	assert.ErrorIs(t, err, domain.ErrNotFound)
	mockRepo.AssertExpectations(t)
}
`

const tmplMocksTest = `package {{.Package}}_test

import (
	"context"

	"github.com/stretchr/testify/mock"

	"{{.Module}}/internal/domain"
)

type Mock{{.Entity}}Repo struct {
	mock.Mock
}

func (m *Mock{{.Entity}}Repo) FindByID(_ context.Context, id string) (*domain.{{.Entity}}, error) {
	args := m.Called(id)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*domain.{{.Entity}}), args.Error(1)
}

func (m *Mock{{.Entity}}Repo) FindAll(_ context.Context, _, _ int) ([]*domain.{{.Entity}}, int64, error) {
	args := m.Called()
	return args.Get(0).([]*domain.{{.Entity}}), int64(len(args.Get(0).([]*domain.{{.Entity}}))), args.Error(1)
}

func (m *Mock{{.Entity}}Repo) FindByName(_ context.Context, name string) (*domain.{{.Entity}}, error) {
	args := m.Called(name)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*domain.{{.Entity}}), args.Error(1)
}

func (m *Mock{{.Entity}}Repo) Create(_ context.Context, entity *domain.{{.Entity}}) error {
	args := m.Called(entity)
	return args.Error(0)
}

func (m *Mock{{.Entity}}Repo) Update(_ context.Context, entity *domain.{{.Entity}}) error {
	args := m.Called(entity)
	return args.Error(0)
}

func (m *Mock{{.Entity}}Repo) Delete(_ context.Context, id string) error {
	args := m.Called(id)
	return args.Error(0)
}
`

const tmplHandlerTest = `package handler_test

import (
	"bytes"
	"context"
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"testing"

	"github.com/go-chi/chi/v5"
	"github.com/stretchr/testify/assert"
	"github.com/stretchr/testify/mock"

	{{.Package}}usecase "{{.Module}}/internal/application/usecase/{{.Package}}"
	"{{.Module}}/internal/domain"
	"{{.Module}}/internal/interface/dto"
	"{{.Module}}/internal/interface/handler"
)

type MockCreate{{.Entity}}UseCase struct{ mock.Mock }

func (m *MockCreate{{.Entity}}UseCase) Execute(_ context.Context, input *{{.Package}}usecase.Create{{.Entity}}Input) (*{{.Package}}usecase.Create{{.Entity}}Output, error) {
	args := m.Called(input)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*{{.Package}}usecase.Create{{.Entity}}Output), args.Error(1)
}

type MockGet{{.Entity}}UseCase struct{ mock.Mock }

func (m *MockGet{{.Entity}}UseCase) Execute(_ context.Context, input *{{.Package}}usecase.Get{{.Entity}}Input) (*{{.Package}}usecase.Get{{.Entity}}Output, error) {
	args := m.Called(input)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*{{.Package}}usecase.Get{{.Entity}}Output), args.Error(1)
}

type MockList{{.Entities}}UseCase struct{ mock.Mock }

func (m *MockList{{.Entities}}UseCase) Execute(_ context.Context, input *{{.Package}}usecase.List{{.Entities}}Input) (*{{.Package}}usecase.List{{.Entities}}Output, error) {
	args := m.Called(input)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*{{.Package}}usecase.List{{.Entities}}Output), args.Error(1)
}

type MockUpdate{{.Entity}}UseCase struct{ mock.Mock }

func (m *MockUpdate{{.Entity}}UseCase) Execute(_ context.Context, id string, input *{{.Package}}usecase.Update{{.Entity}}Input) (*{{.Package}}usecase.Update{{.Entity}}Output, error) {
	args := m.Called(id, input)
	if args.Get(0) == nil {
		return nil, args.Error(1)
	}
	return args.Get(0).(*{{.Package}}usecase.Update{{.Entity}}Output), args.Error(1)
}

type MockDelete{{.Entity}}UseCase struct{ mock.Mock }

func (m *MockDelete{{.Entity}}UseCase) Execute(_ context.Context, input *{{.Package}}usecase.Delete{{.Entity}}Input) error {
	args := m.Called(input)
	return args.Error(0)
}

func Test{{.Entity}}GetAll_Success(t *testing.T) {
	mockUC := new(MockList{{.Entities}}UseCase)
	h := handler.New{{.Entity}}Handler(nil, nil, mockUC, nil, nil)

	respData := &{{.Package}}usecase.List{{.Entities}}Output{
		{{.Entities}}: []*domain.{{.Entity}}{
			{ID: "1", Name: "Test {{.Entity}}"},
		},
		Total:      1,
		Page:       1,
		PageSize:   20,
		TotalPages: 1,
	}
	mockUC.On("Execute", mock.AnythingOfType("*{{.Package}}.List{{.Entities}}Input")).Return(respData, nil)

	req := httptest.NewRequest("GET", "/api/v1/{{.Path}}", nil)
	rec := httptest.NewRecorder()

	r := chi.NewRouter()
	r.Get("/api/v1/{{.Path}}", h.GetAll)
	r.ServeHTTP(rec, req)

	assert.Equal(t, http.StatusOK, rec.Code)

	var resp dto.PaginatedResponse
	json.NewDecoder(rec.Body).Decode(&resp)
	assert.Equal(t, int64(1), resp.Total)

	mockUC.AssertExpectations(t)
}

func Test{{.Entity}}GetByID_Success(t *testing.T) {
	mockUC := new(MockGet{{.Entity}}UseCase)
	h := handler.New{{.Entity}}Handler(nil, mockUC, nil, nil, nil)

	mockUC.On("Execute", &{{.Package}}usecase.Get{{.Entity}}Input{ID: "123"}).Return(
		&{{.Package}}usecase.Get{{.Entity}}Output{{"{"}}{{.Entity}}: &domain.{{.Entity}}{ID: "123", Name: "Test"}}, nil,
	)

	req := httptest.NewRequest("GET", "/api/v1/{{.Path}}/123", nil)
	rec := httptest.NewRecorder()

	r := chi.NewRouter()
	r.Get("/api/v1/{{.Path}}/{id}", h.GetByID)
	r.ServeHTTP(rec, req)

	assert.Equal(t, http.StatusOK, rec.Code)

	var resp dto.{{.Entity}}Response
	json.NewDecoder(rec.Body).Decode(&resp)
	assert.Equal(t, "123", resp.ID)

	mockUC.AssertExpectations(t)
}

func Test{{.Entity}}GetByID_NotFound(t *testing.T) {
	mockUC := new(MockGet{{.Entity}}UseCase)
	h := handler.New{{.Entity}}Handler(nil, mockUC, nil, nil, nil)

	mockUC.On("Execute", &{{.Package}}usecase.Get{{.Entity}}Input{ID: "999"}).Return(nil, domain.ErrNotFound)

	req := httptest.NewRequest("GET", "/api/v1/{{.Path}}/999", nil)
	rec := httptest.NewRecorder()

	r := chi.NewRouter()
	r.Get("/api/v1/{{.Path}}/{id}", h.GetByID)
	r.ServeHTTP(rec, req)

	assert.Equal(t, http.StatusNotFound, rec.Code)

	mockUC.AssertExpectations(t)
}

func Test{{.Entity}}Create_Success(t *testing.T) {
	mockUC := new(MockCreate{{.Entity}}UseCase)
	h := handler.New{{.Entity}}Handler(mockUC, nil, nil, nil, nil)

	mockUC.On("Execute", mock.AnythingOfType("*{{.Package}}.Create{{.Entity}}Input")).Return(
		&{{.Package}}usecase.Create{{.Entity}}Output{{"{"}}{{.Entity}}: &domain.{{.Entity}}{ID: "1", Name: "Test"}}, nil,
	)

	req := httptest.NewRequest("POST", "/api/v1/{{.Path}}", bytes.NewBufferString({{bt}}{"name":"Test","description":"A test"}{{bt}}))
	req.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()

	r := chi.NewRouter()
	r.Post("/api/v1/{{.Path}}", h.Create)
	r.ServeHTTP(rec, req)

	assert.Equal(t, http.StatusCreated, rec.Code)

	mockUC.AssertExpectations(t)
}

func Test{{.Entity}}Update_Success(t *testing.T) {
	mockUC := new(MockUpdate{{.Entity}}UseCase)
	h := handler.New{{.Entity}}Handler(nil, nil, nil, mockUC, nil)

	mockUC.On("Execute", "1", mock.AnythingOfType("*{{.Package}}.Update{{.Entity}}Input")).Return(
		&{{.Package}}usecase.Update{{.Entity}}Output{{"{"}}{{.Entity}}: &domain.{{.Entity}}{ID: "1", Name: "Updated"}}, nil,
	)

	req := httptest.NewRequest("PUT", "/api/v1/{{.Path}}/1", bytes.NewBufferString({{bt}}{"name":"Updated"}{{bt}}))
	req.Header.Set("Content-Type", "application/json")
	rec := httptest.NewRecorder()

	r := chi.NewRouter()
	r.Put("/api/v1/{{.Path}}/{id}", h.Update)
	r.ServeHTTP(rec, req)

	assert.Equal(t, http.StatusOK, rec.Code)

	mockUC.AssertExpectations(t)
}

func Test{{.Entity}}Delete_Success(t *testing.T) {
	mockUC := new(MockDelete{{.Entity}}UseCase)
	h := handler.New{{.Entity}}Handler(nil, nil, nil, nil, mockUC)

	mockUC.On("Execute", &{{.Package}}usecase.Delete{{.Entity}}Input{ID: "1"}).Return(nil)

	req := httptest.NewRequest("DELETE", "/api/v1/{{.Path}}/1", nil)
	rec := httptest.NewRecorder()

	r := chi.NewRouter()
	r.Delete("/api/v1/{{.Path}}/{id}", h.Delete)
	r.ServeHTTP(rec, req)

	assert.Equal(t, http.StatusNoContent, rec.Code)

	mockUC.AssertExpectations(t)
}
`
