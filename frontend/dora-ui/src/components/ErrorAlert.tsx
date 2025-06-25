import { Alert, AlertDescription, AlertTitle } from "@/components/ui/alert"
import { AlertCircle, X } from "lucide-react";

interface ErrorAlertProps {
  title?: string;
  message: string;
  onClose?: () => void;
}

const ErrorAlert = ({ title = "Error", message, onClose }: ErrorAlertProps) => {
  return (
    <Alert variant="destructive" className="relative">
      <AlertCircle className="h-4 w-4" />
      <AlertTitle>{title}</AlertTitle>
      <AlertDescription>{message}</AlertDescription>
      <button
        onClick={onClose}
        className="absolute right-2 top-2 rounded-sm opacity-70 ring-offset-background transition-opacity hover:opacity-100 focus:outline-none focus:ring-2 focus:ring-ring focus:ring-offset-2"
        aria-label="Close error message"
      >
        <X className="h-4 w-4" />
      </button>
    </Alert>
  );
};

export default ErrorAlert;
