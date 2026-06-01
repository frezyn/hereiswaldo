"use client";

import { useState, useCallback, useRef } from "react";
import { Button } from "@workspace/ui/components/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@workspace/ui/components/card";
import { Badge } from "@workspace/ui/components/badge";
import {
  Dialog,
  DialogContent,
  DialogTitle,
} from "@workspace/ui/components/dialog";
import {
  UploadCloud,
  Loader2,
  Search,
  CheckCircle2,
  XCircle,
  ZoomIn,
  X,
  Download,
  Maximize2,
} from "lucide-react";

type Status = "idle" | "loading" | "found" | "not_found" | "error";

export default function Page() {
  const [file, setFile] = useState<File | null>(null);
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);
  const [resultUrl, setResultUrl] = useState<string | null>(null);
  const [status, setStatus] = useState<Status>("idle");
  const [error, setError] = useState<string | null>(null);
  const [isDragging, setIsDragging] = useState(false);
  const [lightboxOpen, setLightboxOpen] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  const selectFile = (selected: File) => {
    setFile(selected);
    setPreviewUrl(URL.createObjectURL(selected));
    setResultUrl(null);
    setStatus("idle");
    setError(null);
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files?.[0]) selectFile(e.target.files[0]);
  };

  const handleDrop = useCallback((e: React.DragEvent) => {
    e.preventDefault();
    setIsDragging(false);
    const dropped = e.dataTransfer.files?.[0];
    if (dropped && dropped.type.startsWith("image/")) selectFile(dropped);
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file) return;

    setStatus("loading");
    setError(null);
    setResultUrl(null);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch("http://localhost:8001/detect", {
        method: "POST",
        body: formData,
      });

      if (!response.ok) throw new Error(`Erro na API: ${response.statusText}`);

      const existWaldo = response.headers.get("X-Exist-Waldo") === "true";
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      setResultUrl(url);
      setStatus(existWaldo ? "found" : "not_found");

      if (existWaldo) {
        setLightboxOpen(true);
      }
    } catch (err) {
      setStatus("error");
      setError(err instanceof Error ? err.message : "Erro inesperado");
    }
  };

  return (
    <div className="min-h-svh flex items-center justify-center bg-background p-4">
      <div className="w-full max-w-lg space-y-4">
        {/* Header */}
        <div className="text-center space-y-1 pb-2">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-2xl bg-primary text-primary-foreground mb-3">
            <Search className="w-7 h-7" />
          </div>
          <h1 className="text-3xl font-bold tracking-tight">Onde está o Wally?</h1>
                </div>

        {/* Upload card */}
        <Card>
          <CardHeader className="pb-3">
            <CardTitle className="text-base">Selecione uma imagem</CardTitle>
            <CardDescription>PNG, JPG ou JPEG</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={handleSubmit} className="space-y-4">
              {/* Drop zone */}
              <div
                onClick={() => inputRef.current?.click()}
                onDragOver={(e) => { e.preventDefault(); setIsDragging(true); }}
                onDragLeave={() => setIsDragging(false)}
                onDrop={handleDrop}
                className={`relative flex flex-col items-center justify-center gap-3 w-full h-48 rounded-xl border-2 border-dashed cursor-pointer transition-all duration-200 select-none
                  ${isDragging
                    ? "border-primary bg-primary/5 scale-[1.01]"
                    : previewUrl
                    ? "border-border"
                    : "border-muted-foreground/30 hover:border-primary/60 hover:bg-muted/40"
                  }`}
              >
                {previewUrl ? (
                  <>
                    <img
                      src={previewUrl}
                      alt="Preview"
                      className="h-full w-full object-contain rounded-lg p-1"
                    />
                    <span className="absolute bottom-2 right-2 text-xs text-muted-foreground bg-background/80 rounded px-1.5 py-0.5 backdrop-blur-sm">
                      Clique para trocar
                    </span>
                  </>
                ) : (
                  <>
                    <div className="p-3 rounded-full bg-muted">
                      <UploadCloud className="w-6 h-6 text-muted-foreground" />
                    </div>
                    <div className="text-center">
                      <p className="text-sm font-medium">
                        Clique ou arraste aqui
                      </p>
                      <p className="text-xs text-muted-foreground mt-0.5">
                        Formatos aceitos: PNG, JPG, JPEG
                      </p>
                    </div>
                  </>
                )}
                <input
                  ref={inputRef}
                  type="file"
                  accept="image/*"
                  className="hidden"
                  onChange={handleFileChange}
                />
              </div>

              <Button
                type="submit"
                className="w-full"
                size="lg"
                disabled={!file || status === "loading"}
              >
                {status === "loading" ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    Procurando Wally...
                  </>
                ) : (
                  <>
                    <Search className="mr-2 h-4 w-4" />
                    Encontrar Wally!
                  </>
                )}
              </Button>
            </form>
          </CardContent>
        </Card>

        {/* Error */}
        {status === "error" && (
          <Card className="border-destructive/40 bg-destructive/5">
            <CardContent className="py-4 flex items-start gap-3">
              <XCircle className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
              <div>
                <p className="text-sm font-semibold text-destructive">Erro ao processar</p>
                <p className="text-xs text-muted-foreground mt-0.5">{error}</p>
              </div>
            </CardContent>
          </Card>
        )}

        {/* Result Card */}
        {resultUrl && (status === "found" || status === "not_found") && (
          <Card className={status === "found" ? "border-green-500/40" : ""}>
            <CardHeader className="pb-3">
              <div className="flex items-center justify-between">
                <CardTitle className="text-base">Resultado</CardTitle>
                <Badge
                  variant={status === "found" ? "default" : "secondary"}
                  className={status === "found" ? "bg-green-600 hover:bg-green-600 text-white" : ""}
                >
                  {status === "found" ? (
                    <><CheckCircle2 className="w-3 h-3 mr-1" />Wally encontrado!</>
                  ) : (
                    <><XCircle className="w-3 h-3 mr-1" />Não encontrado</>
                  )}
                </Badge>
              </div>
            </CardHeader>
            <CardContent className="space-y-3">
              <div
                onClick={() => status === "found" && setLightboxOpen(true)}
                className={`relative rounded-lg overflow-hidden border bg-muted/20 ${status === "found" ? "cursor-zoom-in group" : ""}`}
              >
                <img
                  src={resultUrl}
                  alt="Resultado"
                  className="w-full object-contain max-h-64 transition-transform duration-300 group-hover:scale-[1.02]"
                />
                {status === "found" && (
                  <div className="absolute inset-0 bg-black/0 group-hover:bg-black/20 transition-all flex items-center justify-center">
                    <div className="opacity-0 group-hover:opacity-100 transition-opacity bg-black/60 text-white rounded-full p-2">
                      <ZoomIn className="w-5 h-5" />
                    </div>
                  </div>
                )}
              </div>

              {/* Action buttons */}
              <div className="flex gap-2">
                {status === "found" && (
                  <Button
                    variant="outline"
                    size="sm"
                    className="flex-1"
                    onClick={() => setLightboxOpen(true)}
                  >
                    <Maximize2 className="w-4 h-4 mr-2" />
                    Tela cheia
                  </Button>
                )}
                <Button
                  variant="outline"
                  size="sm"
                  className="flex-1"
                  asChild
                >
                  <a href={resultUrl} download="waldo_resultado.png">
                    <Download className="w-4 h-4 mr-2" />
                    Baixar imagem
                  </a>
                </Button>
              </div>
            </CardContent>
          </Card>
        )}
      </div>

      {/* Lightbox */}
      <Dialog open={lightboxOpen} onOpenChange={setLightboxOpen}>
        <DialogContent showCloseButton={false} className="w-screen h-screen max-w-screen max-h-screen rounded-none p-0 overflow-hidden bg-black/95 border-none flex items-center justify-center">
          <DialogTitle className="sr-only">Resultado - Wally encontrado</DialogTitle>
          {/* Top-right action buttons */}
          <div className="absolute top-3 right-3 z-50 flex items-center gap-2">
            {resultUrl && (
              <a
                href={resultUrl}
                download="waldo_resultado.png"
                className="rounded-full bg-white/10 hover:bg-white/20 p-1.5 text-white transition-colors inline-flex items-center justify-center"
                title="Baixar imagem"
              >
                <Download className="w-5 h-5" />
              </a>
            )}
            <button
              onClick={() => setLightboxOpen(false)}
              className="rounded-full bg-white/10 hover:bg-white/20 p-1.5 text-white transition-colors"
              title="Fechar"
            >
              <X className="w-5 h-5" />
            </button>
          </div>
          {resultUrl && (
            <img
              src={resultUrl}
              alt="Resultado em tela cheia"
              className="w-full h-full object-contain max-h-[95vh]"
            />
          )}
        </DialogContent>
      </Dialog>
    </div>
  );
}
