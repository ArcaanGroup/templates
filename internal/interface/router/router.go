package router

import (
	"log/slog"
	"net/http"

	"github.com/go-chi/chi/v5"
	httpSwagger "github.com/swaggo/http-swagger"
	"github.com/swaggo/swag"

	"go-clean-template/internal/interface/handler"
	"go-clean-template/internal/interface/middleware"
)

func New(
	logger *slog.Logger,
	corsOrigin string,
	userHandler *handler.UserHandler,
	roleHandler *handler.RoleHandler,
) http.Handler {
	r := chi.NewRouter()

	r.Use(middleware.RequestID)
	r.Use(middleware.Recoverer(logger))
	r.Use(middleware.Logger(logger))
	r.Use(middleware.CORS(corsOrigin))

	r.Get("/health", func(w http.ResponseWriter, r *http.Request) {
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(`{"status":"ok"}`))
	})

	r.Get("/openapi.json", func(w http.ResponseWriter, r *http.Request) {
		jsonStr, err := swag.ReadDoc()
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		w.Header().Set("Content-Type", "application/json")
		w.WriteHeader(http.StatusOK)
		w.Write([]byte(jsonStr))
	})

	r.Get("/swagger", func(w http.ResponseWriter, r *http.Request) {
		http.Redirect(w, r, "/swagger/", http.StatusMovedPermanently)
	})
	r.Get("/swagger/*", httpSwagger.Handler(
		httpSwagger.URL("/swagger/doc.json"),
	))

	r.Route("/api/v1", func(r chi.Router) {
		r.Route("/users", func(r chi.Router) {
			r.Get("/", userHandler.GetAll)
			r.Post("/", userHandler.Create)
			r.Get("/{id}", userHandler.GetByID)
			r.Put("/{id}", userHandler.Update)
			r.Delete("/{id}", userHandler.Delete)
			r.Get("/{id}/roles", userHandler.GetUserRoles)
			r.Post("/{id}/roles", userHandler.AssignRoles)
		})

		r.Route("/roles", func(r chi.Router) {
			r.Get("/", roleHandler.GetAll)
			r.Post("/", roleHandler.Create)
			r.Get("/{id}", roleHandler.GetByID)
			r.Put("/{id}", roleHandler.Update)
			r.Delete("/{id}", roleHandler.Delete)
		})
	})

	return r
}
