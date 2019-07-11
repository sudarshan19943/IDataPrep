import { Component, OnInit, Output, EventEmitter } from '@angular/core';
import { DataService } from '../data.service';
import { DomSanitizer } from '@angular/platform-browser';

@Component({
  selector: 'app-csv-file-download',
  templateUrl: './csv-file-download.component.html',
  styleUrls: ['./csv-file-download.component.scss']
})
export class CsvFileDownloadComponent implements OnInit {

  @Output() completed = new EventEmitter<boolean>();
  ready = false;
  downloadFilename = 'IDataPrep_ProcessedDataset.csv';
  base64String;
  downloadURL: any;

  constructor(private dataservice: DataService, private sanitizer: DomSanitizer) { }

  ngOnInit() {
    this.dataservice.cleanedFileReady.subscribe(data => {
      // do awesome stuff with data
      this.base64String = this.ab2str(data);
      this.downloadURL = this.sanitizer.bypassSecurityTrustUrl('data:application/octet-stream;base64,' +
        this.base64String);
      this.ready = true;
      this.dataservice.setStatus('Ready', 'Ready');
    });
  }

  ab2str(buf) {
    return String.fromCharCode.apply(null, new Uint8Array(buf));
  }

  downloadFile() {
    this.completed.emit(true);
  }
}
