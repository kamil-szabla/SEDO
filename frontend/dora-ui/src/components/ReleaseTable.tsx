import * as React from "react"
import { format } from 'date-fns';
import {
  ColumnDef,
  ColumnFiltersState,
  SortingState,
  VisibilityState,
  flexRender,
  getCoreRowModel,
  getFilteredRowModel,
  getPaginationRowModel,
  getSortedRowModel,
  useReactTable,
} from "@tanstack/react-table"

import { Badge } from "@/components/ui/badge"
import { Button } from "@/components/ui/button"
import {
  DropdownMenu,
  DropdownMenuCheckboxItem,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { IconDotsVertical, IconLayoutColumns, IconChevronDown } from "@tabler/icons-react"
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Label } from "@/components/ui/label"
import DatePicker from "@/components/DatePicker"
import type { Release } from '@/lib/api';

interface ReleaseTableProps {
  releases: Release[];
  onEdit: (release: Release) => void;
  onDelete: (id: string) => void;
}

export const ReleaseTable = ({ releases, onEdit, onDelete }: ReleaseTableProps) => {
  const [sorting, setSorting] = React.useState<SortingState>([])
  const [columnFilters, setColumnFilters] = React.useState<ColumnFiltersState>([])
  const [columnVisibility, setColumnVisibility] = React.useState<VisibilityState>({})
  const [rowSelection, setRowSelection] = React.useState({})
  const [startDate, setStartDate] = React.useState<Date | null>(null);
  const [endDate, setEndDate] = React.useState<Date | null>(null);
  const [showDeleteDialog, setShowDeleteDialog] = React.useState(false);
  const [releaseToDelete, setReleaseToDelete] = React.useState<Release | null>(null);
  const [pagination, setPagination] = React.useState({
    pageIndex: 0,
    pageSize: 10,
  })

  // Get unique values for filters
  const platforms = React.useMemo(() => 
    ["all", ...new Set((Array.isArray(releases) ? releases : []).map(r => r.platform))],
    [releases]
  );

  const releaseTypes = React.useMemo(() => 
    ["all", ...new Set((Array.isArray(releases) ? releases : []).map(r => r.release_type))],
    [releases]
  );

  // Filter releases by date range
  const filteredReleases = React.useMemo(() => {
    const safeReleases = Array.isArray(releases) ? releases : [];
    
    return safeReleases.filter((release) => {
      const releaseDate = new Date(release.rollout_date);
      const matchesDate =
        (!startDate || releaseDate >= startDate) &&
        (!endDate || releaseDate <= endDate);
      return matchesDate;
    });
  }, [releases, startDate, endDate]);

  const handleDeleteClick = (release: Release) => {
    setReleaseToDelete(release);
    setShowDeleteDialog(true);
  };

  const handleConfirmDelete = () => {
    if (releaseToDelete) {
      onDelete(releaseToDelete.id);
      setShowDeleteDialog(false);
      setReleaseToDelete(null);
    }
  };

  const columns: ColumnDef<Release>[] = [
    {
      accessorKey: "platform",
      header: ({ column }) => {
        return (
          <Select
            value={(column.getFilterValue() as string) ?? "all"}
            onValueChange={(value) => column.setFilterValue(value)}
          >
            <SelectTrigger className="h-8 w-full min-w-[120px] border-none bg-transparent hover:bg-accent hover:text-accent-foreground px-4">
              <SelectValue placeholder="Platform" />
            </SelectTrigger>
            <SelectContent>
              {platforms.map((platform) => (
                <SelectItem key={platform} value={platform}>
                  {platform === "all" ? "Platform" : platform}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )
      },
      filterFn: (row, id, value) => {
        if (!value) return true;
        return value === "all" || row.getValue(id) === value;
      },
      cell: ({ row }) => (
        <div className="font-medium px-4">{row.getValue("platform")}</div>
      ),
    },
    {
      accessorKey: "release_type",
      header: ({ column }) => {
        return (
          <Select
            value={(column.getFilterValue() as string) ?? "all"}
            onValueChange={(value) => column.setFilterValue(value)}
          >
            <SelectTrigger className="h-8 w-full min-w-[120px] border-none bg-transparent hover:bg-accent hover:text-accent-foreground px-4">
              <SelectValue placeholder="Type" />
            </SelectTrigger>
            <SelectContent>
              {releaseTypes.map((type) => (
                <SelectItem key={type} value={type}>
                  {type === "all" ? "Type" : type}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
        )
      },
      filterFn: (row, id, value) => {
        return value === "all" || row.getValue(id) === value;
      },
      cell: ({ row }) => (
        <div className="w-32 px-4">
          <Badge variant="outline" className="text-muted-foreground px-1.5">
            {row.getValue("release_type")}
          </Badge>
        </div>
      ),
    },
    {
      accessorKey: "is_successful",
      header: ({ column }) => {
        return (
          <Select
            value={(column.getFilterValue() as string) ?? "all"}
            onValueChange={(value) => column.setFilterValue(value)}
          >
            <SelectTrigger className="h-8 w-full min-w-[120px] border-none bg-transparent hover:bg-accent hover:text-accent-foreground px-4">
              <SelectValue placeholder="Status" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">Status</SelectItem>
              <SelectItem value="success">Success</SelectItem>
              <SelectItem value="failed">Failed</SelectItem>
            </SelectContent>
          </Select>
        )
      },
      filterFn: (row, id, value) => {
        if (!value || value === "all") return true;
        const isSuccessful = row.getValue(id) as boolean;
        return (value === "success" && isSuccessful) || (value === "failed" && !isSuccessful);
      },
      cell: ({ row }) => {
        const isSuccessful = row.getValue("is_successful")
        return (
          <div className="px-4">
            <Badge variant={isSuccessful ? "default" : "destructive"}>
              {isSuccessful ? "Success" : "Failed"}
            </Badge>
          </div>
        )
      },
    },
    {
      accessorKey: "version",
      header: () => (
        <div className="px-4">Version</div>
      ),
      cell: ({ row }) => (
        <div className="px-4">{row.getValue("version")}</div>
      ),
    },
    {
      accessorKey: "rollout_date",
      header: () => (
        <div className="px-4">Rollout Date</div>
      ),
      cell: ({ row }) => (
        <div className="px-4">{format(new Date(row.getValue("rollout_date")), 'MMM dd, yyyy')}</div>
      ),
    },
    {
      id: "links",
      header: () => (
        <div className="px-4">Links</div>
      ),
      cell: ({ row }) => {
        const release = row.original
        return (
          <div className="flex flex-col space-y-1 text-xs px-4">
            {release.mcm_link && (
              <a href={release.mcm_link} className="text-blue-600 underline" target="_blank" rel="noopener noreferrer">
                MCM
              </a>
            )}
            {release.ci_job_link && (
              <a href={release.ci_job_link} className="text-blue-600 underline" target="_blank" rel="noopener noreferrer">
                CI Job
              </a>
            )}
            {release.commit_list_link && (
              <a href={release.commit_list_link} className="text-blue-600 underline" target="_blank" rel="noopener noreferrer">
                Commits
              </a>
            )}
          </div>
        )
      },
    },
    {
      id: "actions",
      cell: ({ row }) => {
        const release = row.original
        return (
          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button
                variant="ghost"
                className="flex h-8 w-8 p-0 data-[state=open]:bg-muted"
              >
                <IconDotsVertical className="h-4 w-4" />
                <span className="sr-only">Open menu</span>
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-[160px]">
              <DropdownMenuItem onClick={() => onEdit(release)}>
                Edit
              </DropdownMenuItem>
              <DropdownMenuSeparator />
              <DropdownMenuItem
                onClick={() => handleDeleteClick(release)}
                className="text-red-600"
              >
                Delete
              </DropdownMenuItem>
            </DropdownMenuContent>
          </DropdownMenu>
        )
      },
    },
  ]

  const table = useReactTable({
    data: filteredReleases,
    columns,
    state: {
      sorting,
      columnVisibility,
      rowSelection,
      columnFilters,
      pagination,
    },
    enableRowSelection: false,
    onRowSelectionChange: setRowSelection,
    onSortingChange: setSorting,
    onColumnFiltersChange: setColumnFilters,
    onColumnVisibilityChange: setColumnVisibility,
    onPaginationChange: setPagination,
    getCoreRowModel: getCoreRowModel(),
    getFilteredRowModel: getFilteredRowModel(),
    getPaginationRowModel: getPaginationRowModel(),
    getSortedRowModel: getSortedRowModel(),
  })

  return (
    <>
      <div className="space-y-4">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-4">
            <div>
              <label className="block text-sm font-medium mb-1">Start Date</label>
              <DatePicker onSelect={setStartDate} initialDate={startDate || undefined} />
            </div>
            <div>
              <label className="block text-sm font-medium mb-1">End Date</label>
              <DatePicker onSelect={setEndDate} initialDate={endDate || undefined} />
            </div>
          </div>

          <DropdownMenu>
            <DropdownMenuTrigger asChild>
              <Button variant="outline" size="sm">
                <IconLayoutColumns className="h-4 w-4" />
                <span className="hidden lg:inline ml-2">Customize Columns</span>
                <span className="lg:hidden">Columns</span>
                <IconChevronDown className="h-4 w-4 ml-2" />
              </Button>
            </DropdownMenuTrigger>
            <DropdownMenuContent align="end" className="w-[150px]">
              {table
                .getAllColumns()
                .filter(
                  (column) =>
                    typeof column.accessorFn !== "undefined" &&
                    column.getCanHide()
                )
                .map((column) => {
                  return (
                    <DropdownMenuCheckboxItem
                      key={column.id}
                      className="capitalize"
                      checked={column.getIsVisible()}
                      onCheckedChange={(value) =>
                        column.toggleVisibility(!!value)
                      }
                    >
                      {column.id}
                    </DropdownMenuCheckboxItem>
                  )
                })}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>

        <div className="rounded-md border">
          <Table>
            <TableHeader>
              {table.getHeaderGroups().map((headerGroup) => (
                <TableRow key={headerGroup.id}>
                  {headerGroup.headers.map((header) => {
                    return (
                      <TableHead key={header.id}>
                        {header.isPlaceholder
                          ? null
                          : flexRender(
                              header.column.columnDef.header,
                              header.getContext()
                            )}
                      </TableHead>
                    )
                  })}
                </TableRow>
              ))}
            </TableHeader>
            <TableBody>
              {table.getRowModel().rows?.length ? (
                table.getRowModel().rows.map((row) => (
                  <TableRow
                    key={row.id}
                    data-state={row.getIsSelected() && "selected"}
                  >
                    {row.getVisibleCells().map((cell) => (
                      <TableCell key={cell.id}>
                        {flexRender(cell.column.columnDef.cell, cell.getContext())}
                      </TableCell>
                    ))}
                  </TableRow>
                ))
              ) : (
                <TableRow>
                  <TableCell
                    colSpan={columns.length}
                    className="h-24 text-center"
                  >
                    No results.
                  </TableCell>
                </TableRow>
              )}
            </TableBody>
          </Table>
        </div>

        <div className="flex items-center justify-between px-2">
          <div className="flex items-center gap-2">
            <Label htmlFor="rows-per-page" className="text-sm font-medium whitespace-nowrap">
              Rows per page
            </Label>
            <Select
              value={`${table.getState().pagination.pageSize}`}
              onValueChange={(value) => {
                table.setPageSize(Number(value))
              }}
            >
              <SelectTrigger className="h-8 w-[70px]" id="rows-per-page">
                <SelectValue
                  placeholder={table.getState().pagination.pageSize}
                />
              </SelectTrigger>
              <SelectContent side="top">
                {[10, 20, 30, 40, 50].map((pageSize) => (
                  <SelectItem key={pageSize} value={`${pageSize}`}>
                    {pageSize}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>

          <div className="flex items-center gap-6 lg:gap-8">
            <div className="flex w-[100px] items-center justify-center text-sm font-medium">
              Page {table.getState().pagination.pageIndex + 1} of{" "}
              {table.getPageCount()}
            </div>
            <div className="flex items-center space-x-2">
              <Button
                variant="outline"
                className="h-8 w-8 p-0"
                onClick={() => table.previousPage()}
                disabled={!table.getCanPreviousPage()}
              >
                <span className="sr-only">Go to previous page</span>
                <IconChevronDown className="h-4 w-4 rotate-90" />
              </Button>
              <Button
                variant="outline"
                className="h-8 w-8 p-0"
                onClick={() => table.nextPage()}
                disabled={!table.getCanNextPage()}
              >
                <span className="sr-only">Go to next page</span>
                <IconChevronDown className="h-4 w-4 -rotate-90" />
              </Button>
            </div>
          </div>
        </div>
      </div>

      <Dialog open={showDeleteDialog} onOpenChange={setShowDeleteDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Confirm Delete</DialogTitle>
            <DialogDescription>
              Are you sure you want to delete this release?
            </DialogDescription>
          </DialogHeader>
          {releaseToDelete && (
            <div className="py-4">
              <p><strong>Platform:</strong> {releaseToDelete.platform}</p>
              <p><strong>Version:</strong> {releaseToDelete.version}</p>
              <p><strong>Release Type:</strong> {releaseToDelete.release_type}</p>
              <p><strong>Rollout Date:</strong> {format(new Date(releaseToDelete.rollout_date), 'MMM dd, yyyy')}</p>
            </div>
          )}
          <DialogFooter>
            <Button variant="outline" onClick={() => setShowDeleteDialog(false)}>
              Cancel
            </Button>
            <Button variant="destructive" onClick={handleConfirmDelete}>
              Delete
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </>
  )
}

export default ReleaseTable
