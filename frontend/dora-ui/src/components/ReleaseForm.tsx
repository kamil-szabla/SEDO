import { useState } from 'react';
import { Button } from './ui/button';
import { Label } from './ui/label';
import { Input } from './ui/input';
import { Switch } from './ui/switch';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "./ui/dialog";
import type { CreateReleaseData } from '@/lib/api';

interface Props {
  onSubmit: (data: CreateReleaseData) => void;
  initialData?: CreateReleaseData;
  isEdit?: boolean;
}

const ReleaseForm = ({ onSubmit, initialData, isEdit = false }: Props) => {
  const [platform, setPlatform] = useState(initialData?.platform || '');
  const [releaseType, setReleaseType] = useState(initialData?.release_type || '');
  const [isSuccessful, setIsSuccessful] = useState(initialData?.is_successful ?? true);
  const [version, setVersion] = useState(initialData?.version || '');
  const [rolloutDate, setRolloutDate] = useState(
    initialData?.rollout_date
      ? new Date(initialData.rollout_date).toISOString().slice(0, 10)
      : new Date().toISOString().slice(0, 10)
  );
  const [mcmLink, setMcmLink] = useState(initialData?.mcm_link || '');
  const [ciJobLink, setCiJobLink] = useState(initialData?.ci_job_link || '');
  const [commitListLink, setCommitListLink] = useState(initialData?.commit_list_link || '');
  const [showConfirmDialog, setShowConfirmDialog] = useState(false);

  // Function to get changes between initial and current values
  const getChanges = () => {
    const changes = [];
    
    if (initialData?.platform !== platform) {
      changes.push(`Platform: ${initialData?.platform || 'None'} → ${platform}`);
    }
    if (initialData?.release_type !== releaseType) {
      changes.push(`Release Type: ${initialData?.release_type || 'None'} → ${releaseType}`);
    }
    if (initialData?.is_successful !== isSuccessful) {
      changes.push(`Success Status: ${initialData?.is_successful ? 'Yes' : 'No'} → ${isSuccessful ? 'Yes' : 'No'}`);
    }
    if (initialData?.version !== version) {
      changes.push(`Version: ${initialData?.version || 'None'} → ${version}`);
    }
    if (initialData?.rollout_date !== new Date(rolloutDate).toISOString()) {
      const oldDate = initialData?.rollout_date 
        ? new Date(initialData.rollout_date).toLocaleDateString()
        : 'None';
      const newDate = new Date(rolloutDate).toLocaleDateString();
      changes.push(`Rollout Date: ${oldDate} → ${newDate}`);
    }
    if (initialData?.mcm_link !== mcmLink) {
      changes.push(`MCM Link: ${initialData?.mcm_link || 'None'} → ${mcmLink || 'None'}`);
    }
    if (initialData?.ci_job_link !== ciJobLink) {
      changes.push(`CI Job Link: ${initialData?.ci_job_link || 'None'} → ${ciJobLink || 'None'}`);
    }
    if (initialData?.commit_list_link !== commitListLink) {
      changes.push(`Commit List Link: ${initialData?.commit_list_link || 'None'} → ${commitListLink || 'None'}`);
    }

    return changes;
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (isEdit) {
      setShowConfirmDialog(true);
    } else {
      submitForm();
    }
  };

  const submitForm = () => {
    onSubmit({
      platform,
      release_type: releaseType,
      is_successful: isSuccessful,
      version,
      rollout_date: new Date(rolloutDate).toISOString(),
      mcm_link: mcmLink,
      ci_job_link: ciJobLink,
      commit_list_link: commitListLink,
    });
    setShowConfirmDialog(false);
  };

  return (
    <>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div className="space-y-2">
          <Label htmlFor="platform">Platform</Label>
          <Select value={platform} onValueChange={setPlatform}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Select platform" />
            </SelectTrigger>
            <SelectContent>
              {['Android', 'Samsung', 'Roku', 'Xbox', 'PS4', 'PS5'].map((option) => (
                <SelectItem key={option} value={option}>{option}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="space-y-2">
          <Label htmlFor="releaseType">Release Type</Label>
          <Select value={releaseType} onValueChange={setReleaseType}>
            <SelectTrigger className="w-full">
              <SelectValue placeholder="Select release type" />
            </SelectTrigger>
            <SelectContent>
              {['release', 'rollback'].map((option) => (
                <SelectItem key={option} value={option}>{option}</SelectItem>
              ))}
            </SelectContent>
          </Select>
        </div>

        <div className="flex items-center space-x-4">
          <Label htmlFor="isSuccessful">Was it successful?</Label>
          <Switch
            id="isSuccessful"
            checked={isSuccessful}
            onCheckedChange={setIsSuccessful}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="version">Version</Label>
          <Input
            id="version"
            value={version}
            onChange={(e) => setVersion(e.target.value)}
            required
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="rolloutDate">Rollout Date</Label>
          <Input
            id="rolloutDate"
            type="date"
            value={rolloutDate}
            onChange={(e) => setRolloutDate(e.target.value)}
            required
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="mcmLink">MCM Link</Label>
          <Input
            id="mcmLink"
            type="url"
            value={mcmLink}
            onChange={(e) => setMcmLink(e.target.value)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="ciJobLink">CI Job Link</Label>
          <Input
            id="ciJobLink"
            type="url"
            value={ciJobLink}
            onChange={(e) => setCiJobLink(e.target.value)}
          />
        </div>

        <div className="space-y-2">
          <Label htmlFor="commitListLink">Commit List Link</Label>
          <Input
            id="commitListLink"
            type="url"
            value={commitListLink}
            onChange={(e) => setCommitListLink(e.target.value)}
          />
        </div>

        <Button type="submit" className="mt-4">
          {isEdit ? 'Update Release' : 'Create Release'}
        </Button>
      </form>

      <Dialog open={showConfirmDialog} onOpenChange={setShowConfirmDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Confirm Changes</DialogTitle>
            <DialogDescription>
              Please review the following changes:
            </DialogDescription>
          </DialogHeader>
          <div className="py-4">
            <ul className="list-disc pl-4 space-y-2">
              {getChanges().map((change, index) => (
                <li key={index}>{change}</li>
              ))}
            </ul>
          </div>
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowConfirmDialog(false)}>
              Cancel
            </Button>
            <Button onClick={submitForm}>
              Confirm Changes
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  );
};

export default ReleaseForm;
