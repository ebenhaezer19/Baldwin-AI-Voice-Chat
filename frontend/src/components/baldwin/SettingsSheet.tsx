import {
  Sheet,
  SheetContent,
  SheetDescription,
  SheetHeader,
  SheetTitle,
} from "@/components/ui/sheet";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Switch } from "@/components/ui/switch";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Separator } from "@/components/ui/separator";

interface SettingsSheetProps {
  open: boolean;
  onOpenChange: (open: boolean) => void;
}

export function SettingsSheet({ open, onOpenChange }: SettingsSheetProps) {
  return (
    <Sheet open={open} onOpenChange={onOpenChange}>
      <SheetContent className="w-full overflow-y-auto sm:max-w-md">
        <SheetHeader>
          <SheetTitle>Settings</SheetTitle>
          <SheetDescription>Configure voice, transcription and recording.</SheetDescription>
        </SheetHeader>

        <div className="mt-6 space-y-6 px-4 pb-6">
          <section className="space-y-3">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Voice
            </h3>
            <div className="space-y-1.5">
              <Label>TTS Voice</Label>
              <Select defaultValue="default">
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="default">Default Voice</SelectItem>
                  <SelectItem value="george">George — Male, American (Premium)</SelectItem>
                  <SelectItem value="bella">Bella — Female, Italian (Premium)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5">
              <Label>Response Language</Label>
              <Select defaultValue="en">
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="en">English</SelectItem>
                  <SelectItem value="id">Indonesian</SelectItem>
                  <SelectItem value="mix">Mixed</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </section>

          <Separator />

          <section className="space-y-3">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Speech to Text
            </h3>
            <div className="space-y-1.5">
              <Label>Recognition Language</Label>
              <Select defaultValue="en-IN">
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="en-IN">en-IN</SelectItem>
                  <SelectItem value="hi-IN">hi-IN</SelectItem>
                  <SelectItem value="auto">Auto-detect</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5">
              <div className="flex items-center justify-between">
                <Label>Confidence threshold</Label>
                <span className="font-mono text-xs text-muted-foreground">70%</span>
              </div>
              <Slider defaultValue={[70]} max={100} step={1} />
            </div>
          </section>

          <Separator />

          <section className="space-y-3">
            <h3 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">
              Recording
            </h3>
            <div className="space-y-1.5">
              <Label>Microphone</Label>
              <Select defaultValue="default">
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="default">Default device</SelectItem>
                  <SelectItem value="external">External USB Mic</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="space-y-1.5">
              <Label>Recording quality</Label>
              <Select defaultValue="normal">
                <SelectTrigger>
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="low">Low (8 kHz)</SelectItem>
                  <SelectItem value="normal">Normal (16 kHz)</SelectItem>
                  <SelectItem value="high">High (44.1 kHz)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            <div className="flex items-center justify-between rounded-lg border border-border p-3">
              <div>
                <Label>Voice activity detection</Label>
                <p className="text-xs text-muted-foreground">Auto-stop on silence</p>
              </div>
              <Switch defaultChecked />
            </div>
          </section>
        </div>
      </SheetContent>
    </Sheet>
  );
}
