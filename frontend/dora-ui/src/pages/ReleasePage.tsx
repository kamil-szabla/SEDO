import { useState, useEffect } from 'react';
import ReleaseForm from '@/components/ReleaseForm';
import ReleaseTable from '@/components/ReleaseTable';
import { Button } from "@/components/ui/button";
import ErrorAlert from "@/components/ErrorAlert";
import { releases } from '@/lib/api';
import type { Release, CreateReleaseData } from '@/lib/api';

const ReleasePage = () => {
  const [releaseList, setReleaseList] = useState<Release[]>([]);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [showForm, setShowForm] = useState(false);
  const [editingRelease, setEditingRelease] = useState<Release | null>(null);

  useEffect(() => {
    fetchReleases();
  }, []);

  const fetchReleases = async () => {
    try {
      const data = await releases.getAll();
      setReleaseList(data);
      setError('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load releases');
    } finally {
      setLoading(false);
    }
  };

  const handleCreateRelease = async (data: CreateReleaseData) => {
    try {
      await releases.create(data);
      await fetchReleases();
      setShowForm(false);
      setError('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create release');
    }
  };

  const handleUpdateRelease = async (data: CreateReleaseData) => {
    if (!editingRelease) return;

    try {
      await releases.update(editingRelease.id, data);
      await fetchReleases();
      setEditingRelease(null);
      setShowForm(false);
      setError('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update release');
    }
  };

  const handleDeleteRelease = async (id: string) => {
    try {
      await releases.delete(id);
      await fetchReleases();
      setError('');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete release');
    }
  };

  const handleEdit = (release: Release) => {
    setEditingRelease(release);
    setShowForm(true);
  };

  if (loading) {
    return <div className="flex justify-center items-center min-h-[80vh]">Loading...</div>;
  }

  const getFormInitialData = (release: Release | null): CreateReleaseData | undefined => {
    if (!release) return undefined;
    
    // Format date as YYYY-MM-DD for date input
    const date = new Date(release.rollout_date);
    const formattedDate = date.toISOString().slice(0, 10); // Format as YYYY-MM-DD
    
    return {
      platform: release.platform,
      release_type: release.release_type,
      is_successful: release.is_successful,
      version: release.version,
      rollout_date: formattedDate,
      mcm_link: release.mcm_link || '',
      ci_job_link: release.ci_job_link || '',
      commit_list_link: release.commit_list_link || ''
    };
  };

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold">Releases</h1>
        <Button onClick={() => setShowForm(true)}>Create Release</Button>
      </div>

      {error && <ErrorAlert message={error} onClose={() => setError('')} />}

      {showForm ? (
        <div className="bg-background text-foreground rounded-lg shadow p-6">
          <div className="flex justify-between items-center mb-4">
            <h2 className="text-xl font-semibold">
              {editingRelease ? 'Edit Release' : 'Create New Release'}
            </h2>
            <Button variant="outline" onClick={() => {
              setShowForm(false);
              setEditingRelease(null);
            }}>
              Cancel
            </Button>
          </div>
          <ReleaseForm
            onSubmit={editingRelease ? handleUpdateRelease : handleCreateRelease}
            initialData={getFormInitialData(editingRelease)}
            isEdit={!!editingRelease}
          />
        </div>
      ) : (
        <ReleaseTable
          releases={releaseList}
          onEdit={handleEdit}
          onDelete={handleDeleteRelease}
        />
      )}
    </div>
  );
};

export default ReleasePage;
